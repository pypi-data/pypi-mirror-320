from setuptools import setup, find_packages

# Leer dependencias desde requirements.txt
def load_requirements(filename):
    with open(filename, "r") as f:
        return f.read().splitlines()
    
#print(load_requirements("requirements.txt"))

setup(
    name='Integral_flask_project',
    version='0.0.2',
    description="A powerful Flask extension that provides an integrated solution for building robust web applications with WebSocket support, JWT authentication, database management, email handling, and CORS configuration.",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Conectar Wali SAS',
    author_email='dev@conectarwalisas.com.co',
    url='https://github.com/ConectarWali/Integral-flask-project',
    packages=find_packages(include=["integral_flask_project", "integral_flask_project.*", "src_IFP", "src_IFP.*"]),
    python_requires=">=3.7",
    install_requires=['alembic==1.14.0', 'bidict==0.23.1', 'blinker==1.9.0', 'click==8.1.8', 'colorama==0.4.6', 'Flask==3.1.0', 'Flask-Cors==5.0.0', 'Flask-JWT-Extended==4.7.1', 'Flask-Mail==0.10.0', 'Flask-Migrate==4.0.7', 'Flask-SocketIO==5.5.0', 'Flask-SQLAlchemy==3.1.1', 'greenlet==3.1.1', 'h11==0.14.0', 'itsdangerous==2.2.0', 'Jinja2==3.1.5', 'Mako==1.3.8', 'MarkupSafe==3.0.2', 'PyJWT==2.10.1', 'PyMySQL==1.1.1', 'python-dotenv==1.0.1', 'python-engineio==4.11.2', 'python-socketio==5.12.1', 'redis==5.2.1', 'simple-websocket==1.1.0', 'SQLAlchemy==2.0.36', 'SQLAlchemy-Utils==0.41.2', 'typing_extensions==4.12.2', 'Werkzeug==3.1.3', 'wsproto==1.2.0'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
