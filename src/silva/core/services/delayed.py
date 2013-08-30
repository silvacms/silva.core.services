
from five import grok
from transaction.interfaces import ISavepointDataManager, IDataManagerSavepoint
import transaction
import threading
import operator


class lazy(object):
    """Almost lazy attributes. It will call the method until it
    returns something that isn't None.
    """

    def __init__(self, func, name=None):
        if name is None:
            name = func.__name__
        self.name = name
        self.callable = func

    def __get__(self, inst, class_):
        if inst is None:
            return self

        value = self.callable(inst)
        if value is not None:
            inst.__dict__[self.name] = value

        return value


class Task(object):
    """This is a single task that must be carried at the end of the
    transaction. It can be like updated last modification information,
    or recataloging content. Multiple tasks are sorted upon their
    priority and executed in this order.
    """
    priority = 10

    def __init__(self):
        self.clear()

    def finish(self):
        pass

    def copy(self):
        raise NotImplementedError

    def clear(self):
        pass

    @classmethod
    def get(cls):
        task = manager.get(cls.__name__)
        if task is None:
            task = cls()
            manager.add(task)
        return task


class TaskSavepoint(object):
    """This enable a ZODB savepoint for current tasks.
    """
    grok.implements(IDataManagerSavepoint)

    def __init__(self, tasks):
        self._tasks = tasks

    def restore(self):
        manager.clear()
        for task in self._tasks:
            manager.add(task)


class TaskManager(threading.local):
    """This manages all the task following the current transaction.
    """
    grok.implements(ISavepointDataManager)

    def __init__(self, manager):
        self._manager = manager
        self._followed = False
        self.clear()

    def get(self, name):
        return self._tasks.get(name)

    def add(self, task):
        if not self._followed:
            transaction = self._manager.get()
            transaction.join(self)
            transaction.addBeforeCommitHook(self.beforeCommit)
            self._followed = True
        self._tasks[task.__class__.__name__] = task

    def clear(self):
        self._tasks = {}

    def beforeCommit(self):
        for task in sorted(
            self._tasks.values(),
            key=operator.attrgetter('priority')):
            task.finish()
        self.clear()
        self._followed = False

    def sortKey(self):
        return 'A' * 50

    def savepoint(self):
        tasks = []
        for task in self._tasks.values():
            tasks.append(task.copy())
        return TaskSavepoint(tasks)

    def commit(self, transaction):
        pass

    def abort(self, transaction):
        for task in sorted(
            self._tasks.values(),
            key=operator.attrgetter('priority')):
            task.clear()
        self.clear()
        self._followed = False

    def tpc_begin(self, transaction):
        pass

    def tpc_vote(self, transaction):
        pass

    def tpc_finish(self, transaction):
        pass

    def tpc_abort(self, transaction):
        pass


manager = TaskManager(transaction.manager)
