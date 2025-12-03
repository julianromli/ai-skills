# Flutter Performance Optimization

## Rendering Performance
Keep your app at 60fps.

### 1. Widget Rebuild Optimization
Minimize unnecessary rebuilds.

```dart
// ❌ BAD: Rebuilds entire widget tree
class BadCounter extends StatefulWidget {
  @override
  _BadCounterState createState() => _BadCounterState();
}

class _BadCounterState extends State<BadCounter> {
  int _counter = 0;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text('Count: $_counter'), // Rebuilds every time
        Text('Static text'), // Also rebuilds unnecessarily
        ElevatedButton(
          onPressed: () => setState(() => _counter++),
          child: Text('Increment'),
        ),
      ],
    );
  }
}

// ✅ GOOD: Separate static and dynamic parts
class GoodCounter extends StatelessWidget {
  final int counter;
  final VoidCallback onIncrement;

  const GoodCounter({required this.counter, required this.onIncrement});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        _CounterDisplay(counter: counter), // Only rebuilds counter
        const StaticText(), // Never rebuilds
        ElevatedButton(
          onPressed: onIncrement,
          child: const Text('Increment'), // const widget
        ),
      ],
    );
  }
}

class _CounterDisplay extends StatelessWidget {
  final int counter;

  const _CounterDisplay({required this.counter});

  @override
  Widget build(BuildContext context) {
    return Text('Count: $counter');
  }
}

class StaticText extends StatelessWidget {
  const StaticText();

  @override
  Widget build(BuildContext context) {
    return const Text('Static text'); // const constructor
  }
}
```

### 2. Const Constructors
Use const wherever possible.

```dart
// ❌ BAD: Creates new instances every build
Widget build(BuildContext context) {
  return Column(
    children: [
      Icon(Icons.add),
      Text('Hello'),
      SizedBox(height: 16),
      Padding(padding: EdgeInsets.all(8)),
    ],
  );
}

// ✅ GOOD: Reuses const instances
Widget build(BuildContext context) {
  return const Column(
    children: [
      Icon(Icons.add),
      Text('Hello'),
      SizedBox(height: 16),
      Padding(padding: EdgeInsets.all(8)),
    ],
  );
}
```

### 3. RepaintBoundary
Isolate expensive repaints.

```dart
class ExpensiveWidget extends StatefulWidget {
  @override
  _ExpensiveWidgetState createState() => _ExpensiveWidgetState();
}

class _ExpensiveWidgetState extends State<ExpensiveWidget>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  Widget build(BuildContext context) {
    return RepaintBoundary( // Isolate this widget's repaints
      child: AnimatedBuilder(
        animation: _controller,
        builder: (context, child) {
          return CustomPaint(
            painter: ExpensivePainter(_controller.value),
            child: child,
          );
        },
        child: Container(), // Static child doesn't repaint
      ),
    );
  }
}

class ExpensiveList extends StatelessWidget {
  final List<Item> items;

  const ExpensiveList({required this.items});

  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      itemCount: items.length,
      itemBuilder: (context, index) {
        return RepaintBoundary( // Isolate each list item
          child: ExpensiveListItem(item: items[index]),
        );
      },
    );
  }
}
```

## List Performance
Optimize long lists efficiently.

### 1. ListView.builder vs ListView
Use builder for long lists.

```dart
// ❌ BAD: Builds all items at once
class BadListView extends StatelessWidget {
  final List<Item> items;

  const BadListView({required this.items});

  @override
  Widget build(BuildContext context) {
    return ListView(
      children: items.map((item) => ItemWidget(item: item)).toList(),
    );
  }
}

// ✅ GOOD: Builds items on demand
class GoodListView extends StatelessWidget {
  final List<Item> items;

  const GoodListView({required this.items});

  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      itemCount: items.length,
      itemBuilder: (context, index) {
        return ItemWidget(
          key: ValueKey(items[index].id), // Important for performance
          item: items[index],
        );
      },
    );
  }
}
```

### 2. Item Extent Caching
Cache item dimensions for smooth scrolling.

```dart
class OptimizedListView extends StatelessWidget {
  final List<Item> items;

  const OptimizedListView({required this.items});

  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      itemCount: items.length,
      itemExtent: 80.0, // Fixed height for each item
      itemBuilder: (context, index) {
        return ItemWidget(item: items[index]);
      },
    );
  }
}

// Variable height with prototype
class VariableHeightListView extends StatelessWidget {
  final List<Item> items;

  const VariableHeightListView({required this.items});

  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      itemCount: items.length,
      prototypeItem: ItemWidget(item: items.first), // Prototype for measurement
      itemBuilder: (context, index) {
        return ItemWidget(item: items[index]);
      },
    );
  }
}
```

### 3. Slivers for Advanced Lists
Custom scrolling behavior.

```dart
class SliverListExample extends StatelessWidget {
  final List<Item> items;

  const SliverListExample({required this.items});

  @override
  Widget build(BuildContext context) {
    return CustomScrollView(
      slivers: [
        SliverAppBar(
          expandedHeight: 200,
          floating: true,
          flexibleSpace: FlexibleSpaceBar(
            title: Text('Sliver List'),
          ),
        ),
        SliverList(
          delegate: SliverChildBuilderDelegate(
            (context, index) {
              return ItemWidget(item: items[index]);
            },
            childCount: items.length,
          ),
        ),
        SliverFillRemaining(
          hasScrollBody: false,
          child: Center(child: Text('End of list')),
        ),
      ],
    );
  }
}
```

## Image Performance
Optimize image loading and caching.

### 1. Image Optimization
Efficient image handling.

```dart
class OptimizedImage extends StatelessWidget {
  final String imageUrl;
  final double? width;
  final double? height;

  const OptimizedImage({
    required this.imageUrl,
    this.width,
    this.height,
  });

  @override
  Widget build(BuildContext context) {
    return Image.network(
      imageUrl,
      width: width,
      height: height,
      loadingBuilder: (context, child, loadingProgress) {
        if (loadingProgress == null) return child;
        return Center(
          child: CircularProgressIndicator(
            value: loadingProgress.expectedTotalBytes != null
                ? loadingProgress.cumulativeBytesLoaded /
                    loadingProgress.expectedTotalBytes!
                : null,
          ),
        );
      },
      errorBuilder: (context, error, stackTrace) {
        return Container(
          color: Colors.grey[300],
          child: Icon(Icons.error),
        );
      },
      cacheWidth: width?.toInt(), // Cache at target size
      cacheHeight: height?.toInt(),
      filterQuality: FilterQuality.medium, // Balance quality and performance
    );
  }
}

// Cached network image
class CachedImage extends StatelessWidget {
  final String imageUrl;
  final double? width;
  final double? height;

  const CachedImage({
    required this.imageUrl,
    this.width,
    this.height,
  });

  @override
  Widget build(BuildContext context) {
    return CachedNetworkImage(
      imageUrl: imageUrl,
      width: width,
      height: height,
      placeholder: (context, url) => Container(
        color: Colors.grey[300],
        child: CircularProgressIndicator(),
      ),
      errorWidget: (context, url, error) => Container(
        color: Colors.grey[300],
        child: Icon(Icons.error),
      ),
      memCacheWidth: width?.toInt(),
      memCacheHeight: height?.toInt(),
    );
  }
}
```

### 2. Image Memory Management
Prevent memory leaks.

```dart
class ImageGallery extends StatefulWidget {
  final List<String> imageUrls;

  const ImageGallery({required this.imageUrls});

  @override
  _ImageGalleryState createState() => _ImageGalleryState();
}

class _ImageGalleryState extends State<ImageGallery> {
  final Map<String, ImageProvider> _imageCache = {};

  @override
  void dispose() {
    // Clear image cache
    for (final imageProvider in _imageCache.values) {
      imageProvider.evict();
    }
    super.dispose();
  }

  ImageProvider _getImageProvider(String url) {
    return _imageCache.putIfAbsent(
      url,
      () => NetworkImage(url),
    );
  }

  @override
  Widget build(BuildContext context) {
    return PageView.builder(
      itemCount: widget.imageUrls.length,
      itemBuilder: (context, index) {
        return Image(
          image: _getImageProvider(widget.imageUrls[index]),
          fit: BoxFit.cover,
        );
      },
    );
  }
}
```

## Animation Performance
Smooth 60fps animations.

### 1. Animation Optimization
Efficient animation patterns.

```dart
// ❌ BAD: Animates expensive widgets
class BadAnimation extends StatefulWidget {
  @override
  _BadAnimationState createState() => _BadAnimationState();
}

class _BadAnimationState extends State<BadAnimation>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _controller,
      builder: (context, child) {
        return Column( // Rebuilds entire column
          children: [
            Text('Expensive widget 1'),
            Text('Expensive widget 2'),
            Text('Expensive widget 3'),
            Transform.rotate( // Only this needs animation
              angle: _controller.value * 2 * math.pi,
              child: Icon(Icons.refresh),
            ),
          ],
        );
      },
    );
  }
}

// ✅ GOOD: Isolate animated parts
class GoodAnimation extends StatefulWidget {
  @override
  _GoodAnimationState createState() => _GoodAnimationState();
}

class _GoodAnimationState extends State<GoodAnimation>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        const Text('Static widget 1'), // const, no rebuild
        const Text('Static widget 2'), // const, no rebuild
        const Text('Static widget 3'), // const, no rebuild
        AnimatedBuilder(
          animation: _controller,
          builder: (context, child) {
            return Transform.rotate(
              angle: _controller.value * 2 * math.pi,
              child: child, // Pass child to avoid rebuilding
            );
          },
          child: const Icon(Icons.refresh), // const widget
        ),
      ],
    );
  }
}
```

### 2. Performance-Friendly Animations
Choose the right animation type.

```dart
// Use implicit animations for simple cases
class SimpleAnimation extends StatefulWidget {
  final bool isVisible;

  const SimpleAnimation({required this.isVisible});

  @override
  Widget build(BuildContext context) {
    return AnimatedOpacity(
      opacity: isVisible ? 1.0 : 0.0,
      duration: Duration(milliseconds: 200),
      curve: Curves.easeOut,
      child: Container(
        color: Colors.blue,
        height: 100,
        width: 100,
      ),
    );
  }
}

// Use explicit animations for complex cases
class ComplexAnimation extends StatefulWidget {
  @override
  _ComplexAnimationState createState() => _ComplexAnimationState();
}

class _ComplexAnimationState extends State<ComplexAnimation>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _scaleAnimation;
  late Animation<Color?> _colorAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: Duration(milliseconds: 800),
      vsync: this,
    );

    _scaleAnimation = Tween<double>(
      begin: 1.0,
      end: 1.2,
    ).animate(CurvedAnimation(
      parent: _controller,
      curve: Curves.easeInOut,
    ));

    _colorAnimation = ColorTween(
      begin: Colors.blue,
      end: Colors.red,
    ).animate(CurvedAnimation(
      parent: _controller,
      curve: Curves.easeInOut,
    ));
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _controller,
      builder: (context, child) {
        return Transform.scale(
          scale: _scaleAnimation.value,
          child: Container(
            color: _colorAnimation.value,
            height: 100,
            width: 100,
          ),
        );
      },
    );
  }
}
```

## Memory Management
Prevent memory leaks and bloat.

### 1. Controller Management
Proper disposal of controllers.

```dart
class ProperControllerManagement extends StatefulWidget {
  @override
  _ProperControllerManagementState createState() =>
      _ProperControllerManagementState();
}

class _ProperControllerManagementState
    extends State<ProperControllerManagement>
    with SingleTickerProviderStateMixin {
  late AnimationController _animationController;
  late TextEditingController _textController;
  late ScrollController _scrollController;
  late PageController _pageController;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      duration: Duration(milliseconds: 300),
      vsync: this,
    );
    _textController = TextEditingController();
    _scrollController = ScrollController();
    _pageController = PageController();
  }

  @override
  void dispose() {
    // Always dispose controllers
    _animationController.dispose();
    _textController.dispose();
    _scrollController.dispose();
    _pageController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        AnimatedBuilder(
          animation: _animationController,
          builder: (context, child) {
            return Transform.rotate(
              angle: _animationController.value * 2 * math.pi,
              child: child,
            );
          },
          child: Icon(Icons.refresh),
        ),
        TextField(controller: _textController),
        Expanded(
          child: ListView.builder(
            controller: _scrollController,
            itemCount: 100,
            itemBuilder: (context, index) {
              return ListTile(title: Text('Item $index'));
            },
          ),
        ),
        PageView.builder(
          controller: _pageController,
          itemCount: 3,
          itemBuilder: (context, index) {
            return Center(child: Text('Page $index'));
          },
        ),
      ],
    );
  }
}
```

### 2. Stream Management
Proper stream subscription handling.

```dart
class StreamManagement extends StatefulWidget {
  @override
  _StreamManagementState createState() => _StreamManagementState();
}

class _StreamManagementState extends State<StreamManagement> {
  final StreamController<String> _streamController = StreamController<String>();
  late StreamSubscription _subscription;
  int _counter = 0;

  @override
  void initState() {
    super.initState();
    _subscription = _streamController.stream.listen((data) {
      setState(() {
        _counter++;
      });
    });

    // Start emitting data
    Timer.periodic(Duration(seconds: 1), (timer) {
      _streamController.add('Data ${timer.tick}');
    });
  }

  @override
  void dispose() {
    // Always cancel subscriptions
    _subscription.cancel();
    _streamController.close();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text('Counter: $_counter'),
        ElevatedButton(
          onPressed: () {
            _streamController.add('Manual data');
          },
          child: Text('Add Data'),
        ),
      ],
    );
  }
}
```

## Performance Profiling
Use Flutter DevTools effectively.

### 1. Performance Overlay
Built-in performance debugging.

```dart
class PerformanceApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      // Enable performance overlay
      checkerboardRasterCacheImages: true, // Show raster cache
      checkerboardOffscreenLayers: true, // Show offscreen layers
      showPerformanceOverlay: true, // Show performance metrics
      home: MyHomePage(),
    );
  }
}
```

### 2. Custom Performance Monitor
Track app performance.

```dart
class PerformanceMonitor extends StatefulWidget {
  final Widget child;

  const PerformanceMonitor({required this.child});

  @override
  _PerformanceMonitorState createState() => _PerformanceMonitorState();
}

class _PerformanceMonitorState extends State<PerformanceMonitor>
    with WidgetsBindingObserver {
  final List<Duration> _frameTimes = [];
  Timer? _timer;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    _startMonitoring();
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    _timer?.cancel();
    super.dispose();
  }

  void _startMonitoring() {
    _timer = Timer.periodic(Duration(seconds: 1), (timer) {
      if (_frameTimes.isNotEmpty) {
        final averageFrameTime = _frameTimes.reduce(
          (a, b) => a + b,
        ) / _frameTimes.length;

        final fps = 1000 / averageFrameTime.inMilliseconds;

        print('Average FPS: ${fps.toStringAsFixed(1)}');
        _frameTimes.clear();
      }
    });
  }

  @override
  void didHaveMetrics(Duration frameTime) {
    _frameTimes.add(frameTime);
  }

  @override
  Widget build(BuildContext context) {
    return widget.child;
  }
}
```

## Best Practices Summary

### DO ✅
- Use `const` constructors for static widgets
- Implement `RepaintBoundary` for complex animations
- Use `ListView.builder` for long lists
- Dispose controllers and subscriptions properly
- Cache image providers and dimensions
- Profile with Flutter DevTools regularly

### DON'T ❌
- Rebuild entire widget trees unnecessarily
- Create new instances in build methods
- Use regular `ListView` for long lists
- Forget to dispose controllers
- Load full-resolution images for thumbnails
- Ignore performance warnings

### Performance Checklist
- [ ] All static widgets use `const` constructors
- [ ] Expensive widgets wrapped in `RepaintBoundary`
- [ ] Lists use `builder` constructors
- [ ] Controllers properly disposed
- [ ] Images optimized with caching
- [ ] Animations run at 60fps
- [ ] Memory usage is stable
- [ ] No jank during scrolling