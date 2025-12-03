# Flutter Widget Patterns

## Composition Patterns

### 1. Builder Pattern
Use when you need context-dependent widgets or performance optimization.

```dart
// LayoutBuilder for responsive design
LayoutBuilder(
  builder: (context, constraints) {
    if (constraints.maxWidth > 600) {
      return _buildDesktopLayout();
    } else {
      return _buildMobileLayout();
    }
  },
)

// FutureBuilder for async data
FutureBuilder<String>(
  future: _fetchData(),
  builder: (context, snapshot) {
    if (snapshot.connectionState == ConnectionState.waiting) {
      return CircularProgressIndicator();
    }
    if (snapshot.hasError) {
      return Text('Error: ${snapshot.error}');
    }
    return Text(snapshot.data ?? 'No data');
  },
)
```

### 2. State Management Pattern
Choose the right approach for your app complexity.

```dart
// Simple state with StatefulWidget
class CounterWidget extends StatefulWidget {
  @override
  _CounterWidgetState createState() => _CounterWidgetState();
}

class _CounterWidgetState extends State<CounterWidget> {
  int _counter = 0;

  void _increment() => setState(() => _counter++);

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text('Count: $_counter'),
        ElevatedButton(
          onPressed: _increment,
          child: Text('Increment'),
        ),
      ],
    );
  }
}

// Complex state with Provider/Bloc
class CounterProvider extends ChangeNotifier {
  int _counter = 0;
  int get counter => _counter;

  void increment() {
    _counter++;
    notifyListeners();
  }
}

// Usage
ChangeNotifierProvider(
  create: (_) => CounterProvider(),
  child: Consumer<CounterProvider>(
    builder: (context, provider, child) {
      return Text('Count: ${provider.counter}');
    },
  ),
)
```

### 3. Custom Widget Pattern
Create reusable, themed components.

```dart
class CustomCard extends StatelessWidget {
  final Widget child;
  final EdgeInsets? padding;
  final Color? backgroundColor;
  final double? elevation;

  const CustomCard({
    required this.child,
    this.padding,
    this.backgroundColor,
    this.elevation,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: elevation ?? 4,
      color: backgroundColor ?? Theme.of(context).cardColor,
      child: Padding(
        padding: padding ?? const EdgeInsets.all(16),
        child: child,
      ),
    );
  }
}

// Usage with theme integration
class ThemedCard extends StatelessWidget {
  final Widget child;
  final EdgeInsets? padding;

  const ThemedCard({required this.child, this.padding});

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Theme.of(context).shadowColor.withOpacity(0.1),
            blurRadius: 8,
            offset: Offset(0, 2),
          ),
        ],
      ),
      child: Padding(
        padding: padding ?? const EdgeInsets.all(16),
        child: child,
      ),
    );
  }
}
```

## Layout Patterns

### 1. Responsive Grid
Adaptive grid layouts for different screen sizes.

```dart
class ResponsiveGrid extends StatelessWidget {
  final List<Widget> children;
  final int mobileColumns;
  final int tabletColumns;
  final int desktopColumns;

  const ResponsiveGrid({
    required this.children,
    this.mobileColumns = 1,
    this.tabletColumns = 2,
    this.desktopColumns = 3,
  });

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        int columns;
        if (constraints.maxWidth < 600) {
          columns = mobileColumns;
        } else if (constraints.maxWidth < 1200) {
          columns = tabletColumns;
        } else {
          columns = desktopColumns;
        }

        return GridView.count(
          crossAxisCount: columns,
          children: children,
        );
      },
    );
  }
}
```

### 2. Expandable Section
Collapsible content with smooth animations.

```dart
class ExpandableSection extends StatefulWidget {
  final Widget title;
  final Widget content;
  final bool initiallyExpanded;

  const ExpandableSection({
    required this.title,
    required this.content,
    this.initiallyExpanded = false,
  });

  @override
  _ExpandableSectionState createState() => _ExpandableSectionState();
}

class _ExpandableSectionState extends State<ExpandableSection>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _animation;
  bool _isExpanded = false;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: Duration(milliseconds: 300),
      vsync: this,
    );
    _animation = CurvedAnimation(
      parent: _controller,
      curve: Curves.easeInOut,
    );

    if (widget.initiallyExpanded) {
      _isExpanded = true;
      _controller.value = 1.0;
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _toggle() {
    setState(() {
      _isExpanded = !_isExpanded;
      if (_isExpanded) {
        _controller.forward();
      } else {
        _controller.reverse();
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        GestureDetector(
          onTap: _toggle,
          child: Container(
            padding: EdgeInsets.all(16),
            child: Row(
              children: [
                Expanded(child: widget.title),
                AnimatedRotation(
                  turns: _isExpanded ? 0.5 : 0,
                  duration: Duration(milliseconds: 300),
                  child: Icon(Icons.expand_more),
                ),
              ],
            ),
          ),
        ),
        SizeTransition(
          sizeFactor: _animation,
          child: widget.content,
        ),
      ],
    );
  }
}
```

## Interaction Patterns

### 1. Swipeable List Item
Gestures for list interactions.

```dart
class SwipeableListItem extends StatefulWidget {
  final Widget child;
  final VoidCallback? onSwipeLeft;
  final VoidCallback? onSwipeRight;
  final Widget? leftAction;
  final Widget? rightAction;

  const SwipeableListItem({
    required this.child,
    this.onSwipeLeft,
    this.onSwipeRight,
    this.leftAction,
    this.rightAction,
  });

  @override
  _SwipeableListItemState createState() => _SwipeableListItemState();
}

class _SwipeableListItemState extends State<SwipeableListItem>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _animation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: Duration(milliseconds: 200),
      vsync: this,
    );
    _animation = CurvedAnimation(
      parent: _controller,
      curve: Curves.easeOut,
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onPanUpdate: (details) {
        if (details.delta.dx > 0 && widget.onSwipeRight != null) {
          _controller.forward();
        } else if (details.delta.dx < 0 && widget.onSwipeLeft != null) {
          _controller.forward();
        }
      },
      onPanEnd: (details) {
        if (_controller.value > 0.5) {
          if (details.velocity.pixelsPerSecond.dx > 0) {
            widget.onSwipeRight?.call();
          } else {
            widget.onSwipeLeft?.call();
          }
        }
        _controller.reverse();
      },
      child: Stack(
        children: [
          widget.child,
          if (widget.leftAction != null)
            Positioned.fill(
              child: AnimatedBuilder(
                animation: _animation,
                builder: (context, child) {
                  return Transform.translate(
                    offset: Offset(_animation.value * -100, 0),
                    child: widget.leftAction,
                  );
                },
              ),
            ),
          if (widget.rightAction != null)
            Positioned.fill(
              child: AnimatedBuilder(
                animation: _animation,
                builder: (context, child) {
                  return Transform.translate(
                    offset: Offset(_animation.value * 100, 0),
                    child: widget.rightAction,
                  );
                },
              ),
            ),
        ],
      ),
    );
  }
}
```

### 2. Pull to Refresh
Custom pull-to-refresh implementation.

```dart
class CustomPullToRefresh extends StatefulWidget {
  final Future<void> Function() onRefresh;
  final Widget child;
  final double refreshTriggerOffset;

  const CustomPullToRefresh({
    required this.onRefresh,
    required this.child,
    this.refreshTriggerOffset = 80.0,
  });

  @override
  _CustomPullToRefreshState createState() => _CustomPullToRefreshState();
}

class _CustomPullToRefreshState extends State<CustomPullToRefresh>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _animation;
  bool _isRefreshing = false;
  double _dragOffset = 0.0;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: Duration(milliseconds: 300),
      vsync: this,
    );
    _animation = CurvedAnimation(
      parent: _controller,
      curve: Curves.easeInOut,
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  Future<void> _handleRefresh() async {
    setState(() => _isRefreshing = true);
    await widget.onRefresh();
    setState(() => _isRefreshing = false);
    _controller.reverse();
  }

  @override
  Widget build(BuildContext context) {
    return RefreshIndicator(
      onRefresh: _handleRefresh,
      child: CustomScrollView(
        physics: AlwaysScrollableScrollPhysics(),
        slivers: [
          SliverToBoxAdapter(
            child: AnimatedBuilder(
              animation: _animation,
              builder: (context, child) {
                return Transform.translate(
                  offset: Offset(0, _animation.value * _dragOffset),
                  child: child,
                );
              },
              child: widget.child,
            ),
          ),
        ],
      ),
    );
  }
}
```

## Performance Patterns

### 1. ListView Optimization
Efficient list rendering with builders.

```dart
class OptimizedListView extends StatelessWidget {
  final List<Item> items;

  const OptimizedListView({required this.items});

  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      itemCount: items.length,
      itemBuilder: (context, index) {
        return _buildItem(items[index]);
      },
      // Use const keys for better performance
      key: ValueKey('list_${items.length}'),
    );
  }

  Widget _buildItem(Item item) {
    return Card(
      key: ValueKey(item.id), // Unique key for each item
      child: ListTile(
        title: Text(item.title),
        subtitle: Text(item.description),
        // Use const for static widgets
        leading: const Icon(Icons.article),
      ),
    );
  }
}
```

### 2. RepaintBoundary
Isolate expensive widget rebuilds.

```dart
class ComplexAnimation extends StatefulWidget {
  @override
  _ComplexAnimationState createState() => _ComplexAnimationState();
}

class _ComplexAnimationState extends State<ComplexAnimation>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  Widget build(BuildContext context) {
    return RepaintBoundary(
      child: AnimatedBuilder(
        animation: _controller,
        builder: (context, child) {
          return CustomPaint(
            painter: ComplexPainter(_controller.value),
            child: child,
          );
        },
        child: Container(), // Static child doesn't rebuild
      ),
    );
  }
}