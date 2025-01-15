from IPython.core.magic import Magics, magics_class, cell_magic


@magics_class
class EvalsMagics(Magics):
    def __init__(self, shell):
        super().__init__(shell)
        try:
            import ipytest
            from ipytest._impl import ipytest_magic

            self.ipytest = ipytest
            self.ipytest_magic = ipytest_magic

            ipytest.autoconfig(
                run_in_thread=True,  # pyright: ignore [reportArgumentType]
                addopts=[  # pyright: ignore [reportArgumentType]
                    "--assert=plain",
                    "--run-eval",
                    "--run-eval-analysis",
                    "-s",  # Don't capture output
                    "--log-cli-level=ERROR",
                ],
            )
        except ImportError:
            raise ImportError(
                "ipytest is required to use this magic command. Please install it with: pip install ipytest"
            )

    @cell_magic
    def ipytest_evals(self, line, cell):
        """
        Execute pytest evaluations in the current IPython cell.

        Usage:
            %%pytest_evals [optional arguments]
            def test_something():
                assert True
        """
        # Force reload to ensure fresh test environment
        from pytest_harvest import FIXTURE_STORE

        FIXTURE_STORE.clear()

        # Run the cell content as tests
        self.ipytest_magic(line, cell)


def load_ipython_extension(ipython):
    """
    Register the magic when the extension loads.
    """
    ipython.register_magics(EvalsMagics)
