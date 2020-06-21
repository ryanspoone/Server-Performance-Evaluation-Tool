"""Enforce code style with YAPF."""

import os
import subprocess
import unittest


class StyleTest(unittest.TestCase):
  """Enforce code style requirements."""

  def testCodeStyle(self):
    """Check YAPF style enforcement runs cleanly."""
    file_path = os.path.abspath(os.path.dirname(__file__))
    spet_path = os.path.join(file_path, '..', '..', 'spet')
    config_path = os.path.join(file_path, '..', '..', '.style.yapf')
    try:
      subprocess.check_output(
          ['yapf', '--style', config_path, '--diff', '-r', spet_path])
    except subprocess.CalledProcessError as e:
      if hasattr(e, 'output'):
        raise Exception(
            'From the root directory of the repository, run '
            '"yapf --style {0:s} -i -r {1:s}" to correct '
            'these problems: {2:s}'.format(
                config_path, spet_path, e.output.decode('utf-8')))
      raise


if __name__ == '__main__':
  unittest.main()
