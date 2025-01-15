[![PyPI version](https://img.shields.io/pypi/v/pytest-evals.svg)](https://pypi.org/p/pytest-evals)
[![License](https://img.shields.io/github/license/AlmogBaku/pytest-evals.svg)](https://github.com/AlmogBaku/pytest-evals/blob/main/LICENSE)
[![Issues](https://img.shields.io/github/issues/AlmogBaku/pytest-evals.svg)](https://github.com/AlmogBaku/pytest-evals/issues)
[![Stars](https://img.shields.io/github/stars/AlmogBaku/pytest-evals.svg)](https://github.com/AlmogBaku/pytest-evals/stargazers)

# pytest-evals

A minimal pytest plugin to evaluate LLM applications easily. Run tests at scale, collect metrics, analyze results and
seamlessly integrate with your CI/CD pipeline.

- ✨ Run evaluations at scale
- 🔄 Two-phase execution: cases first, analysis second
- 📊 Built-in result collection and metrics calculation
- 🚀 Parallel execution support (with [`pytest-xdist`](https://pytest-xdist.readthedocs.io/))

```python
@pytest.mark.eval(name="my_eval")
@pytest.mark.parametrize("case", TEST_DATA)
def test_agent(case, eval_bag):
    # save whatever you need in the bag. You'll have access to it later in the analysis phase
    eval_bag.prediction = agent.predict(case["input"])


@pytest.mark.eval_analysis(name="my_eval")
def test_analysis(eval_results):
    print(f"F1 Score: {calculate_f1(eval_results):.2%}")
```

Evaluations are easy - just write tests! no need to reinvent the wheel with complex DSLs or frameworks.

## Why Another Eval Tool?

**Evaluations are just tests.** No need for complex frameworks or DSLs. `pytest-evals` is minimal by design:

- Use `pytest` - the tool you already know
- Keep tests and evaluations together
- Focus on logic, not infrastructure

It just collects your results and lets you analyze them as a whole. Nothing more, nothing less.

## Install

```bash
pip install pytest-evals
```

## Quick Start

Here's a complete example evaluating a simple classifier:

```python
import pytest

TEST_DATA = [
    {"text": "I need to debug this Python code", "label": True},
    {"text": "The cat jumped over the lazy dog", "label": False},
    {"text": "My monitor keeps flickering", "label": True},
]


@pytest.fixture
def classifier():
    def classify(text: str) -> bool:
        # In real-life, we would use a more sophisticated model like an LLM for this :P
        computer_keywords = {'debug', 'python', 'code', 'monitor'}
        return any(keyword in text.lower() for keyword in computer_keywords)

    return classify


@pytest.mark.eval(name="computer_classifier")
@pytest.mark.parametrize("case", TEST_DATA)
def test_classifier(case: dict, eval_bag, classifier):
    eval_bag.input_text = case["text"]
    eval_bag.label = case["label"]
    eval_bag.prediction = classifier(case["text"])
    assert eval_bag.prediction == eval_bag.label


@pytest.mark.eval_analysis(name="computer_classifier")
def test_analysis(eval_results):
    total = len(eval_results)
    correct = sum(1 for r in eval_results if r.result.prediction == r.result.label)
    accuracy = correct / total

    print(f"Accuracy: {accuracy:.2%}")
    assert accuracy >= 0.7
```

Run it:

```bash
# Run test cases
pytest --run-eval

# Analyze results
pytest --run-eval-analysis
```

## How It Works

Built on top of [pytest-harvest](https://smarie.github.io/python-pytest-harvest/), pytest-evals splits evaluation into
two phases:

1. **Evaluation Phase**: Run all test cases, collecting results and metrics in `eval_bag`. The results are saved in a
   temporary file to allow the analysis phase to access them.
2. **Analysis Phase**: Process all results at once through `eval_results` to calculate final metrics

This split allows you to:

- Run evaluations in parallel (since the analysis test MUST run after all cases are done, we must run them separately)
- Make pass/fail decisions on the overall evaluation results instead of individual test failures (by passing the
  `--supress-failed-exit-code --run-eval` flags)
- Collect comprehensive metrics

**Note**: When running evaluation tests, the rest of your test suite will not run. This is by design to keep the results
clean and focused.

### Working with a notebook

It's also possible to run evaluations from a notebook. To do that, simply
install [ipytest](https://github.com/chmp/ipytest), and
reload the `pytest_harvest` plugin in your tests. This will allow you to run evaluations directly from a notebook:

You can see an example of this in the [`example/example_notebook.ipynb`](example/example_notebook.ipynb) notebook.

## Production Use

### Managing Test Data (Evaluation Set)

It's recommended to use a CSV file to store test data. This makes it easier to manage large datasets and allows you to
communicate with non-technical stakeholders.

To do this, you can use `pandas` to read the CSV file and pass the test cases as parameters to your tests using
`@pytest.mark.parametrize` 🙃 :

```python
import pandas as pd
import pytest

test_data = pd.read_csv("tests/testdata.csv")


@pytest.mark.eval(name="my_eval")
@pytest.mark.parametrize("case", test_data.to_dict(orient="records"))
def test_agent(case, eval_bag, agent):
    eval_bag.prediction = agent.run(case["input"])
```

In case you need to select a subset of the test data (e.g., a golden set), you can simply define an environment variable
to indicate that, and filter the data with `pandas`.

### CI Integration

Run tests and analysis as separate steps:

```yaml
evaluate:
  steps:
    - run: pytest --run-eval -n auto --supress-failed-exit-code  # Run cases in parallel
    - run: pytest --run-eval-analysis  # Analyze results
```

Use `--supress-failed-exit-code` with `--run-eval` - let the analysis phase determine success/failure. **If all your
cases pass, your evaluation set is probably too small!**

### Running in Parallel

As your evaluation set grows, you may want to run your test cases in parallel. To do this, install
[`pytest-xdist`](https://pytest-xdist.readthedocs.io/). `pytest-evals` will support that out of the box 🚀.

```bash
run: pytest --run-eval -n auto
```