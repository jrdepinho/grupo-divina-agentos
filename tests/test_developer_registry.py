from agentos.developer.registry import (
    PHASE_1_CAPABILITIES,
    PHASE_2_CAPABILITIES,
    list_capabilities,
)


def test_capabilities_are_registered():
    capabilities = set(list_capabilities())

    assert "code.write_file" in capabilities
    assert "code.patch_file" in capabilities
    assert "python.compile" in capabilities
    assert "tests.run" in capabilities
    assert "git.status" in capabilities
    assert "git.diff" in capabilities
    assert "git.commit" in capabilities
    assert "git.push" in capabilities


def test_git_write_is_phase2_only():
    assert "git.commit" not in PHASE_1_CAPABILITIES
    assert "git.push" not in PHASE_1_CAPABILITIES
    assert "git.commit" in PHASE_2_CAPABILITIES
    assert "git.push" in PHASE_2_CAPABILITIES
