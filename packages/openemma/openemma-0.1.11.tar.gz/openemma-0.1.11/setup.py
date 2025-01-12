from setuptools import setup, find_packages

setup(
    name='openemma',
    version='0.1.11',
    packages=find_packages(),
    description="OpenEMMA is an open-source implementation of Waymo's End-to-End Multimodal Model for Autonomous Driving (EMMA).",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Shuo Xing',
    author_email='shuoxing@tamu.edu',
    url='https://github.com/taco-group/OpenEMMA',
    install_requires=[
        'torch>=1.8.1',
        'torchvision>=0.9.1',
        'matplotlib>=3.2.2',
        'numpy>=1.18.5',
        'opencv-python>=4.1.2',
        'Pillow>=7.1.2',
        'PyYAML>=5.3.1',
        'requests>=2.23.0',
        'scipy>=1.4.1',
        'tqdm>=4.41.0',
        'gdown',
        'flask',
        'Werkzeug',
        'argparse',
        'transformers>=4.46.2',
        'ultralytics',
        'qwen_vl_utils',
        'pyquaternion',
        'nuscenes-devkit',
        'openai',
        'pandas>=1.1.4',
        'seaborn>=0.11.0',
        'thop'  # FLOPs computation
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8',
    ],
    entry_points={
        'console_scripts': [
            'openemma=openemma.main:main_function',
        ],
    },
)