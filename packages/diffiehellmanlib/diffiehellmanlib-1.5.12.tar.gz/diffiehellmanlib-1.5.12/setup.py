import os
import platform
from setuptools import setup, find_packages
from setuptools.command.install import install
import shutil

class CustomInstallCommand(install):
    """Custom installation command to handle library selection and copying."""
    def run(self):
        system = platform.system()
        arch = platform.machine()

        # List of required libraries based on OS and architecture
        if system == "Windows":
            if arch in ["AMD64", "x86_64"]:
                libs = [
                    "dif_helm_x64.dll",
                    "libcrypto-3-x64.dll"
                ]
            elif arch in ["i386", "i686"]:
                libs = [
                    "dif_helm_x86.dll",
                    "libcrypto-3.dll"
                ]
            else:
                raise RuntimeError(f"Unsupported Windows architecture: {arch}")
        elif system == "Linux":
            if arch in ["AMD64", "x86_64"]:
                libs = ["dif_helm_x64.so"]
            elif arch in ["i386", "i686"]:
                libs = ["dif_helm_x86.so"]
            elif "arm" in arch:
                if "64" in arch:
                    libs = ["dif_helm_arm64.so"]
                else:
                    libs = ["dif_helm_armv7.so"]
            else:
                raise RuntimeError(f"Unsupported Linux architecture: {arch}")
        else:
            raise RuntimeError(f"Unsupported operating system: {system}")

        # Copy libraries to the target installation directory
        target_dir = os.path.join(self.install_lib,"diffiehellmanlib", "libs")
        os.makedirs(target_dir, exist_ok=True)
        for lib in libs:
            shutil.copy(lib, target_dir)
            print(f"Library installed: {lib} -> {target_dir}")

        # Continue with standard installation
        super().run()

# Read the contents of README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='diffiehellmanlib',
    version='1.5.12',
    description='Simplified number generation library for the Diffie-Hellman protocol.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Konstantin Gorshkov',
    author_email='kostya_gorshkov_06@vk.com',
    url='https://github.com/kostya2023/diffie_hellman_lib',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        '': ['diffiehellmanlib/libs/*.dll', 'diffiehellmanlib/libs/*.so'],  # Include all required libraries
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: Implementation :: CPython',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
    ],
    python_requires='>=3.6',
    cmdclass={
        'install': CustomInstallCommand,
    },
)
