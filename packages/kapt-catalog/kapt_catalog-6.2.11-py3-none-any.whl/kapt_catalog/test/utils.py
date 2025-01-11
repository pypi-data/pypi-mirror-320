import contextlib
from unittest import mock


# Originaly comes from mock-django (https://github.com/dcramer/mock-django)
@contextlib.contextmanager
def mock_signal_receiver(signal, wraps=None, **kwargs):
    """
    Temporarily attaches a receiver to the provided ``signal`` within the scope
    of the context manager.

    The mocked receiver is returned as the ``as`` target of the ``with``
    statement.

    To have the mocked receiver wrap a callable, pass the callable as the
    ``wraps`` keyword argument. All other keyword arguments provided are passed
    through to the signal's ``connect`` method.

    >>> with mock_signal_receiver(post_save, sender=Model) as receiver:
    >>>     Model.objects.create()
    >>>     assert receiver.call_count = 1
    """
    if wraps is None:
        wraps = lambda *args, **kwargs: None  # noqa

    receiver = mock.Mock(wraps=wraps)
    signal.connect(receiver, **kwargs)
    yield receiver
    signal.disconnect(receiver)


def get_differences(initial, other, attr_name, values_list):
    """
    Given two objects, the name of an attribute handled and a list of attribute names that are
    present on the related object, try to find the differences between these two objects.
    """
    differences = {}

    initial_rel = getattr(initial, attr_name)
    other_rel = getattr(other, attr_name)

    if initial_rel is not None and other_rel is not None:
        initial_values = [getattr(initial_rel, attr) for attr in values_list]
        other_values = [getattr(other_rel, attr) for attr in values_list]
        if initial_values != other_values:
            differences = {attr_name: other_values}
    elif (initial_rel is None and other_rel) or (other_rel is None and initial_rel):
        differences = {attr_name: other_rel}

    return differences


def get_set_differences(initial, other, attr_set_name, values_list):
    """
    Given two objects, the name of an attribute handled by a manager and a list of attribute names
    that are present on the related objects, try to find the differences between these two objects.
    """
    differences = {}

    initial_list = getattr(initial, attr_set_name).values_list(*values_list)
    other_list = getattr(other, attr_set_name).values_list(*values_list)

    differences_list = [x for x in list(set(other_list) ^ set(initial_list))]
    if differences_list:
        differences = {attr_set_name: differences_list}

    return differences
