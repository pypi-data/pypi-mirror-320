import os
import tempfile
import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from readium import ReadConfig, Readium
from readium.core import is_git_url, clone_repository
from pypdf import PdfWriter

# Test data setup
TEST_CONTENT = """# Test Document
This is a test document for Readium.
"""

@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)

@pytest.fixture
def sample_files(temp_dir):
    # Create test files with different extensions
    files = {
        'doc1.md': '# Test Markdown',
        'doc2.txt': 'Plain text file',
        'code.py': 'def test(): pass',
        'large.md': 'x' * (5 * 1024 * 1024 + 1),  # Exceeds default size limit
        'config.json': '{"key": "value"}',
        '.hidden': 'hidden file',
        'document.pdf': 'PDF content',  # Para test de MarkItDown
    }
    
    for name, content in files.items():
        file_path = temp_dir / name
        file_path.write_text(content)
    
    # Create test directories
    (temp_dir / 'node_modules').mkdir()
    # Crear el archivo test.js dentro de node_modules
    (temp_dir / 'node_modules' / 'test.js').write_text('console.log("test")')
    
    (temp_dir / 'docs').mkdir()
    (temp_dir / 'docs' / 'guide.md').write_text('# Guide')
    
    return temp_dir

@pytest.fixture
def sample_pdf(sample_files):
    """Create a real PDF file for testing"""
    # Crear un PDF simple
    writer = PdfWriter()
    # Añadir una página en blanco
    writer.add_blank_page(width=72, height=72)
    
    pdf_path = sample_files / "document.pdf"
    with open(pdf_path, "wb") as output_file:
        writer.write(output_file)
    
    return pdf_path

def test_read_config_defaults():
    """Test ReadConfig initialization with default values"""
    config = ReadConfig()
    assert config.max_file_size == 5 * 1024 * 1024  # 5MB
    assert '.git' in config.exclude_dirs
    assert '.md' in config.include_extensions
    assert config.target_dir is None
    assert not config.use_markitdown
    assert '.pdf' in config.markitdown_extensions
    assert not config.debug

def test_read_config_custom():
    """Test ReadConfig initialization with custom values"""
    config = ReadConfig(
        max_file_size=1024,
        target_dir='docs',
        use_markitdown=True,
        debug=True
    )
    assert config.max_file_size == 1024
    assert config.target_dir == 'docs'
    assert config.use_markitdown
    assert config.debug

def test_is_git_url():
    """Test git URL detection"""
    assert is_git_url('https://github.com/user/repo.git')
    assert is_git_url('https://github.com/user/repo')
    assert is_git_url('https://gitlab.com/user/repo')
    assert not is_git_url('http://example.com')
    assert not is_git_url('/local/path')

@patch('subprocess.run')
def test_clone_repository(mock_run, temp_dir):
    """Test repository cloning functionality"""
    url = 'https://github.com/user/repo.git'
    clone_repository(url, str(temp_dir))
    mock_run.assert_called_once()
    assert '--depth=1' in mock_run.call_args[0][0]

def test_readium_init():
    """Test Readium initialization"""
    reader = Readium()
    assert reader.config is not None
    assert reader.markitdown is None

    reader_with_markitdown = Readium(ReadConfig(use_markitdown=True))
    assert reader_with_markitdown.markitdown is not None

def test_should_process_file(sample_files):
    """Test file processing criteria"""
    reader = Readium()
    
    # Should process normal markdown file
    assert reader.should_process_file(sample_files / 'doc1.md')
    
    # Should not process files in excluded directories
    assert not reader.should_process_file(sample_files / 'node_modules' / 'test.js')
    
    # Should not process files exceeding size limit
    assert not reader.should_process_file(sample_files / 'large.md')
    
    # Should process files with allowed extensions
    assert reader.should_process_file(sample_files / 'code.py')

def test_read_docs_local(sample_files):
    """Test reading documentation from local directory"""
    reader = Readium()
    summary, tree, content = reader.read_docs(sample_files)
    
    assert 'Files processed:' in summary
    assert 'Documentation Structure:' in tree
    assert '# Test Markdown' in content
    assert 'Plain text file' in content

def test_read_docs_with_target_dir(sample_files):
    """Test reading documentation with target directory specified"""
    config = ReadConfig(target_dir='docs')
    reader = Readium(config)
    summary, tree, content = reader.read_docs(sample_files)
    
    assert 'Target directory: docs' in summary
    assert 'guide.md' in tree
    assert '# Guide' in content
    assert 'doc1.md' not in content  # Should not include files outside target dir

@patch('readium.core.clone_repository')
def test_read_docs_git(mock_clone, temp_dir):
    """Test reading documentation from git repository"""
    # Configurar el mock para que lance una excepción
    mock_clone.side_effect = ValueError("Failed to clone repository")
    reader = Readium()
    
    with pytest.raises(ValueError):
        reader.read_docs('https://github.com/fake/repo.git')
    
    mock_clone.assert_called_once()

@patch('readium.core.MarkItDown')  # Cambiamos el path del patch
def test_read_docs_with_markitdown(mock_markitdown, sample_files, sample_pdf):
    """Test reading documentation with MarkItDown integration"""
    # Configurar el mock
    mock_instance = Mock()
    mock_instance.convert.return_value = Mock(text_content="Converted content")
    mock_markitdown.return_value = mock_instance
    
    # Añadimos algunos logs para debug
    print("\nDebug: Mock setup complete")
    
    # Configurar Readium con MarkItDown solo para PDFs
    config = ReadConfig(
        use_markitdown=True,
        markitdown_extensions={'.pdf'},
        include_extensions=set(),  # No procesar otros tipos de archivo
        debug=True  # Activar logs de debug
    )
    reader = Readium(config)
    print(f"Debug: Reader markitdown instance: {reader.markitdown}")
    
    summary, tree, content = reader.read_docs(sample_files)
    print(f"Debug: Mock convert called: {mock_instance.convert.called}")
    print(f"Debug: Mock convert call args: {mock_instance.convert.call_args_list}")
    
    assert 'Using MarkItDown for compatible files' in summary
    assert mock_instance.convert.called
    assert str(sample_pdf) in [args[0] for args, _ in mock_instance.convert.call_args_list]
    assert 'Converted content' in content

# Integration tests

def test_full_directory_scan(sample_files):
    """Integration test for full directory scanning"""
    config = ReadConfig(
        max_file_size=1024 * 1024,  # 1MB
        exclude_dirs={'node_modules'},
        include_extensions={'.md', '.txt', '.py'},
        debug=True
    )
    reader = Readium(config)
    summary, tree, content = reader.read_docs(sample_files)
    
    # Verify summary
    assert 'Path analyzed:' in summary
    assert 'Files processed:' in summary
    
    # Verify tree structure
    assert 'Documentation Structure:' in tree
    assert 'doc1.md' in tree
    assert 'doc2.txt' in tree
    assert 'code.py' in tree
    
    # Verify content
    assert '# Test Markdown' in content
    assert 'Plain text file' in content
    assert 'def test():' in content