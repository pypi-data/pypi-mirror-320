import unittest
import importlib.util
import subprocess
import sys
from pathlib import Path
import click

class TestInstallation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Store the current working directory
        cls.cwd = Path.cwd()
        
    def test_package_installable(self):
        """Test if the package can be installed in a fresh environment"""
        with click.progressbar(length=2, label='Testing installation') as bar:
            # Try importing the package
            spec = importlib.util.find_spec('dnaviz')
            bar.update(1)
            
            self.assertIsNotNone(spec, "dnaviz package not found. Installation may have failed.")
            
            # Try importing main components (add your main modules here)
            try:
                import dnaviz
                # Add other important modules you want to test
                # import dnaviz.visualization
                # import dnaviz.analysis
            except ImportError as e:
                self.fail(f"Failed to import dnaviz: {str(e)}")
            
            bar.update(1)

    def test_dependencies_installed(self):
        """Test if all required dependencies are installed"""
        with open(self.cwd / 'requirements.txt', 'r') as f:
            requirements = [line.strip() for line in f if line.strip() 
                          and not line.startswith('#')]

        results = []
        with click.progressbar(requirements, label='Checking dependencies') as deps:
            for requirement in deps:
                package_name = requirement.split('==')[0].split('>=')[0].split('<=')[0]
                spec = importlib.util.find_spec(package_name)
                results.append((package_name, spec is not None))

        # Display results in a table
        click.echo("\nDependency Check Results:")
        click.echo("-" * 40)
        click.echo(f"{'Package':<30} {'Status':<10}")
        click.echo("-" * 40)
        for package, installed in results:
            status = click.style("✓", fg="green") if installed else click.style("✗", fg="red")
            click.echo(f"{package:<30} {status:<10}")
        
        # Assert all dependencies are installed
        missing = [pkg for pkg, installed in results if not installed]
        self.assertEqual(missing, [], f"Missing dependencies: {', '.join(missing)}")

    def test_version(self):
        """Test if version is properly set"""
        import dnaviz
        self.assertTrue(hasattr(dnaviz, '__version__'), "Package does not have a version number")
        self.assertIsInstance(dnaviz.__version__, str, "Version number should be a string")

def main():
    unittest.main(verbosity=2)

if __name__ == '__main__':
    main() 