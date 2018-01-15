Sortable.create(foo, {
  group: 'foo',
  animation: 100
});

Sortable.create(bar, {
  group: 'bar',
  animation: 100
});

Sortable.create(qux, {
  group: {
    name: 'qux',
    put: ['foo', 'bar']
  },
  animation: 100
});
