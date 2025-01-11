import elements
import pytest


class TestCheckpoint:

  def test_basic(self, tmpdir):
    path = elements.Path(tmpdir)
    foo = Foo(42)
    cp = elements.Checkpoint(path)
    cp.foo = foo
    foo.value = 12
    cp.save()
    assert cp.latest() == path / (path / 'latest').read_text()
    filenames = set(x.name for x in cp.latest().glob('*'))
    assert filenames == {'foo.pkl', 'done'}
    del cp
    foo = Foo(42)
    cp = elements.Checkpoint(tmpdir)
    cp.foo = foo
    cp.load()
    assert foo.value == 12

  def test_load_or_save(self, tmpdir):
    path = elements.Path(tmpdir)
    for restart in range(3):
      foo = Foo(42)
      cp = elements.Checkpoint(path, keep=3)
      cp.foo = foo
      cp.load_or_save()
      assert foo.value == 42 + restart
      foo.value += 1
      cp.save()

  def test_keep(self, tmpdir, keep=3):
    path = elements.Path(tmpdir)
    cp = elements.Checkpoint(path, keep=keep)
    cp.foo = Foo(0)
    for i in range(1, 6):
      cp.foo.value = i
      cp.save()
      filenames = set(x.name for x in path.glob('*'))
      filenames.remove('latest')
      assert len(filenames) == min(i, keep)
    cp.load()
    assert cp.foo.value == 5

  def test_step(self, tmpdir):
    path = elements.Path(tmpdir)
    step = elements.Counter(0)
    cp = elements.Checkpoint(path, step=step, keep=3)
    cp.foo = Foo(0)
    for _ in range(5):
      cp.foo.value = int(step)
      cp.save()
      step.increment()
    filenames = set(x.name for x in path.glob('*'))
    filenames.remove('latest')
    steps = set(int(x.split('-')[1]) for x in filenames)
    assert steps == {2, 3, 4}

  def test_generator(self, tmpdir):

    class Bar:
      def __init__(self, values):
        self.values = values
      def save(self):
        for value in self.values:
          yield {'value': value}
      def load(self, data):
        for i, shard in enumerate(data):
          self.values[i] = shard['value']

    path = elements.Path(tmpdir)
    cp = elements.Checkpoint(path)
    cp.bar = Bar([42, 12, 26])
    cp.save()
    filenames = set(x.name for x in cp.latest().glob('*'))
    assert filenames == {
        'bar-000000.pkl',
        'bar-000001.pkl',
        'bar-000002.pkl',
        'done',
    }
    del cp
    cp = elements.Checkpoint(path)
    cp.bar = Bar([0, 0, 0])
    cp.load()
    assert cp.bar.values == [42, 12, 26]

  def test_saveable_inline(self, tmpdir):
    path = elements.Path(tmpdir)
    cp = elements.Checkpoint(path)
    foo = [42]
    cp.foo = elements.Saveable(
        save=lambda: foo[0],
        load=lambda x: [foo.clear(), foo.insert(0, x)])
    cp.save()
    foo = [12]
    cp.load()
    assert foo == [42]

  def test_saveable_inherit(self, tmpdir):

    class Bar(elements.Saveable):
      def __init__(self, value):
        super().__init__(['value'])
        self.value = value

    path = elements.Path(tmpdir)
    bar = Bar(42)
    cp = elements.Checkpoint(path)
    cp.bar = bar
    cp.save()
    bar.value = 12
    cp.load()
    assert bar.value == 42

  def test_path(self, tmpdir):
    path = elements.Path(tmpdir)
    cp = elements.Checkpoint()
    cp.foo = Foo(42)
    cp.save(path / 'inner')
    assert set(path.glob('*')) == {path / 'inner'}
    cp.foo.value = 12
    cp.load(path / 'inner')
    assert cp.foo.value == 42

  def test_keys(self, tmpdir):
    path = elements.Path(tmpdir)
    cp = elements.Checkpoint(path)
    cp.foo = Foo(42)
    cp.bar = Foo(12)
    cp.save(keys=['bar'])
    filenames = set(x.name for x in cp.latest().glob('*'))
    assert filenames == {'bar.pkl', 'done'}
    cp.foo.value = 0
    cp.bar.value = 0
    cp.load(keys=['bar'])
    assert cp.foo.value == 0
    assert cp.bar.value == 12
    with pytest.raises(KeyError):
      cp.load()


class Foo:

  def __init__(self, value):
    self.value = value

  def save(self):
    return {'value': self.value}

  def load(self, data):
    self.value = data['value']
