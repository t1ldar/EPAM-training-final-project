import pytest

from rss_parser.argument_parser.argument_parser import (NegativeOrZeroLimitArgError,
                                                        validate_limit_arg)


@pytest.mark.parametrize('expected_exception, limit_arg', [(ValueError, 'a'),
                                                           (NegativeOrZeroLimitArgError, -1),
                                                           (NegativeOrZeroLimitArgError, 0)]
                         )
def test_validate_limit_arg(expected_exception, limit_arg):
    with pytest.raises(expected_exception):
        validate_limit_arg(limit_arg)
