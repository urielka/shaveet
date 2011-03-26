from setuptools import setup

setup(name='shaveet', 
      version='0.1', 
      packages=['shaveet'],
      package_data={'shaveet': ['static/*.js']},
      install_requires = ['gevent>=0.13','python-daemon','wsgi-jsonrpc','static'],
      extras_require = {'process title':  ["setproctitle"]},
      author = "Uriel Katz",
      author_email = "uriel.katz@gmail.com",
      description = "Shaveet comet server",
      license = "MIT",
      keywords = "comet gevent server",
      url = "https://github.com/urielka/shaveet",
      download_url = "https://github.com/urielka/shaveet/downloads",
      zip_safe = False,
      scripts = ['scripts/shaveet'],
)
