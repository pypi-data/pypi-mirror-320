import pytest
from pathlib import Path
import json

pytest_plugins = "pytester"

# Test data
SAMPLE_TEST_DATA = [
    {"input": "test1", "expected": True},
    {"input": "test2", "expected": False},
]

# Fixtures
@pytest.fixture
def temp_output_dir(tmp_path):
    """Create a temporary directory for test outputs"""
    return tmp_path / "test-output"

@pytest.fixture
def mock_classifier():
    """Mock classifier for testing"""
    def classify(text: str) -> bool:
        return "test1" in text
    return classify

# Basic functionality tests
def test_eval_marker_configuration(pytester):
    """Test that the eval marker is properly configured"""
    pytester.makepyfile("""
        import pytest
        
        @pytest.mark.eval(name="test_eval")
        def test_simple():
            assert True
    """)

    result = pytester.runpytest("--run-eval")
    result.assert_outcomes(passed=1)

def test_eval_analysis_marker_configuration(pytester):
    """Test that the eval_analysis marker is properly configured"""
    pytester.makepyfile("""
        import pytest
        
        @pytest.mark.eval_analysis(name="test_eval")
        def test_analysis(eval_results):
            assert len(eval_results) == 0
    """)

    result = pytester.runpytest("--run-eval-analysis")
    result.assert_outcomes(passed=1)

def test_missing_name_in_eval_marker(pytester):
    """Test that eval marker requires name parameter"""
    pytester.makepyfile("""
        import pytest
        
        @pytest.mark.eval
        def test_simple():
            assert True
    """)

    result = pytester.runpytest("--run-eval")
    assert result.ret != 0

# Integration tests
def test_complete_evaluation_workflow(pytester):
    """Test a complete evaluation workflow with both eval and analysis phases"""
    # Create test file with both evaluation and analysis
    pytester.makepyfile("""
        import pytest
        
        TEST_DATA = [
            {"input": "test1", "expected": True},
            {"input": "test2", "expected": False},
        ]
        
        @pytest.fixture
        def mock_classifier():
            def classify(text: str) -> bool:
                return "test1" in text
            return classify
        
        @pytest.mark.eval(name="test_classifier")
        @pytest.mark.parametrize("case", TEST_DATA)
        def test_classifier(case, eval_bag, mock_classifier):
            eval_bag.input = case["input"]
            eval_bag.expected = case["expected"]
            eval_bag.prediction = mock_classifier(case["input"])
            assert eval_bag.prediction == case["expected"]
        
        @pytest.mark.eval_analysis(name="test_classifier")
        def test_analysis(eval_results):
            assert len(eval_results) == 2
            correct = sum(1 for r in eval_results 
                        if r.result.prediction == r.result.expected)
            accuracy = correct / len(eval_results)
            assert accuracy == 1.0
    """)

    # Run evaluation phase
    result_eval = pytester.runpytest("--run-eval")
    result_eval.assert_outcomes(passed=2, skipped=1)

    # Run analysis phase
    result_analysis = pytester.runpytest("--run-eval-analysis")
    result_analysis.assert_outcomes(passed=1, skipped=2)

def test_output_file_creation(pytester, temp_output_dir):
    """Test that results are properly saved to output file"""
    temp_output_dir.mkdir(exist_ok=True)

    pytester.makepyfile("""
        import pytest
        
        @pytest.mark.eval(name="test_eval")
        def test_simple(eval_bag):
            eval_bag.result = "test_value"
            assert True
    """)

    result = pytester.runpytest("--run-eval", f"--out-path={temp_output_dir}", "-v")
    result.assert_outcomes(passed=1)

    results_file = Path(temp_output_dir) / "eval-results-raw.json"
    assert results_file.exists()

    with open(results_file) as f:
        results = json.load(f)
        assert any("test_value" in str(v.get("fixtures").get("eval_bag")) for v in results.values())

def test_suppress_failed_exit_code(pytester):
    """Test that --suppress-failed-exit-code works as expected"""
    pytester.makepyfile("""
        import pytest
        
        @pytest.mark.eval(name="test_eval")
        def test_failing():
            assert False
    """)

    # Without suppress flag
    result1 = pytester.runpytest("--run-eval")
    result1.assert_outcomes(failed=1)
    assert result1.ret != 0

    # With suppress flag
    result2 = pytester.runpytest("--run-eval", "--supress-failed-exit-code")
    result2.assert_outcomes(failed=1)
    assert result2.ret == 0

def test_eval_results_fixture(pytester):
    """Test that eval_results fixture provides correct data"""
    pytester.makepyfile("""
        import pytest
        
        @pytest.mark.eval(name="test_eval")
        def test_data(eval_bag):
            eval_bag.value = 42
            assert True
        
        @pytest.mark.eval_analysis(name="test_eval")
        def test_analysis(eval_results):
            assert len(eval_results) == 1
            assert eval_results[0].result.value == 42
    """)

    # Run both phases
    pytester.runpytest("--run-eval")
    result = pytester.runpytest("--run-eval-analysis")
    result.assert_outcomes(passed=1, skipped=1)

# Error handling tests
def test_invalid_marker_combination(pytester):
    """Test that a test cannot have both eval and eval_analysis markers"""
    pytester.makepyfile("""
        import pytest
        
        @pytest.mark.eval(name="test")
        @pytest.mark.eval_analysis(name="test")
        def test_invalid():
            assert True
    """)

    result = pytester.runpytest("--run-eval")
    assert result.ret != 0

def test_eval_results_fixture_protection(pytester):
    """Test that eval_results fixture is only available in analysis tests"""
    pytester.makepyfile("""
        import pytest
        
        @pytest.mark.eval(name="test_eval")
        def test_invalid(eval_results):
            assert True
    """)

    result = pytester.runpytest("--run-eval")
    assert result.ret != 0