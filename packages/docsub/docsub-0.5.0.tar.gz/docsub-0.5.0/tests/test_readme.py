from subprocess import check_output


def test_readme(data_path, python, monkeypatch):
    monkeypatch.chdir(data_path)

    # stdout
    result = check_output([python, '-m', 'docsub', 'README.md'], text=True)
    assert result == (data_path / '__result__.md').read_text()

    # in-place
    check_output([python, '-m', 'docsub', '-i', 'README.md'])
    result = (data_path / 'README.md').read_text()
    assert result == (data_path / '__result__.md').read_text()
