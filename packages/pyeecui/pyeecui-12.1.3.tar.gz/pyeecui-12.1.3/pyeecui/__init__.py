# -*- coding: utf-8 -*-

"""
pyeecui supplies a `EventEmitter` class that is similar to the
`EventEmitter` class from Node.js. In addition, it supplies the subclasses
`AsyncIOEventEmitter`, `TwistedEventEmitter` and `ExecutorEventEmitter`
for supporting async and threaded execution with asyncio, twisted, and
concurrent.futures Executors respectively, as supported by the environment.

# Example

```text
In [1]: from pyeecui.base import EventEmitter

In [2]: ee = EventEmitter()

In [3]: @ee.on('event')
   ...: def event_handler():
   ...:     print('BANG BANG')
   ...:

In [4]: ee.emit('event')
BANG BANG

In [5]:
```

"""

from pyeecui.base import EventEmitter, PyeeError, PyeeException

__all__ = ["EventEmitter", "PyeeError", "PyeeException"]
