from setuptools import find_packages, setup

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="safeai-face",
    version="0.0.3.1",
    description="SafeAI face detection and face retrieval library using milvus vector DB",
    long_description = long_description,
    long_description_content_type='text/markdown',
    author="paradise999",
    author_email="choirock6416@gamil.com",
    url="https://github.com/safeai-kr/safeai-face.git",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'pymilvus>=2.4.2',
        'timm',
        'torch==2.5.1',
        'torchvision==0.20.1',
        'scikit-learn',
        'pillow',
        'numpy==2.0.2',
        'opencv-python==4.10.0.84',
        'ultralytics==8.3.4',
        'onnxruntime==1.19.2',
        'onnxruntime-gpu==1.19.2',
        'opencv-contrib-python',
        'lapx>=0.5.2'
    ],
    keywords=["SafeAI", "safeai", "face", "face detection", "face retrieval"],
    python_requires='>=3.10.8'
)
