from setuptools import setup, find_packages

setup(
    name='CTkDateEntry',
    version='0.1.2',
    packages=find_packages(),
    author='Claudio Morais',
    author_email='jc.morais86@gmail.com',
    description='A customized dateentry to facilitate date selection in graphical interfaces.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/ClaudioM1386/CTkDateEntry-0.1.2',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    install_requires=[
        'requests',
        'customtkinter',  # Inclui a dependência do CustomTkinter
        'ctkcalendar',    # Inclui a dependência do CTkCalendar, se for um pacote separado
    ],
)
