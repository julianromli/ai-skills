# Flutter Animation Patterns

## Implicit Animations
Simple animations with minimal code.

### 1. AnimatedContainer
Smooth property transitions.

```dart
class AnimatedCard extends StatefulWidget {
  final bool isSelected;
  final Widget child;

  const AnimatedCard({required this.isSelected, required this.child});

  @override
  _AnimatedCardState createState() => _AnimatedCardState();
}

class _AnimatedCardState extends State<AnimatedCard> {
  bool _isHovered = false;

  @override
  Widget build(BuildContext context) {
    return MouseRegion(
      onEnter: (_) => setState(() => _isHovered = true),
      onExit: (_) => setState(() => _isHovered = false),
      child: AnimatedContainer(
        duration: Duration(milliseconds: 200),
        curve: Curves.easeInOut,
        width: _isHovered ? 200 : 180,
        height: _isHovered ? 120 : 100,
        decoration: BoxDecoration(
          color: widget.isSelected
            ? Theme.of(context).primaryColor
            : (_isHovered ? Colors.grey[200] : Colors.grey[100]),
          borderRadius: BorderRadius.circular(_isHovered ? 16 : 8),
          boxShadow: _isHovered
            ? [BoxShadow(color: Colors.black26, blurRadius: 8, offset: Offset(0, 4))]
            : [BoxShadow(color: Colors.black12, blurRadius: 2, offset: Offset(0, 1))],
        ),
        child: widget.child,
      ),
    );
  }
}
```

### 2. AnimatedOpacity & AnimatedScale
Fade and scale effects.

```dart
class FadeInButton extends StatefulWidget {
  final String text;
  final VoidCallback onPressed;
  final Duration delay;

  const FadeInButton({
    required this.text,
    required this.onPressed,
    this.delay = Duration.zero,
  });

  @override
  _FadeInButtonState createState() => _FadeInButtonState();
}

class _FadeInButtonState extends State<FadeInButton> {
  bool _isVisible = false;

  @override
  void initState() {
    super.initState();
    Future.delayed(widget.delay, () {
      if (mounted) setState(() => _isVisible = true);
    });
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedOpacity(
      opacity: _isVisible ? 1.0 : 0.0,
      duration: Duration(milliseconds: 600),
      curve: Curves.easeOut,
      child: AnimatedScale(
        scale: _isVisible ? 1.0 : 0.8,
        duration: Duration(milliseconds: 600),
        curve: Curves.elasticOut,
        child: ElevatedButton(
          onPressed: widget.onPressed,
          child: Text(widget.text),
        ),
      ),
    );
  }
}
```

## Explicit Animations
Fine-grained control with AnimationController.

### 1. Custom Tween Animation
Controlled property animation.

```dart
class AnimatedProgress extends StatefulWidget {
  final double progress; // 0.0 to 1.0
  final Color color;
  final Duration duration;

  const AnimatedProgress({
    required this.progress,
    this.color = Colors.blue,
    this.duration = const Duration(milliseconds: 800),
  });

  @override
  _AnimatedProgressState createState() => _AnimatedProgressState();
}

class _AnimatedProgressState extends State<AnimatedProgress>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _animation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: widget.duration,
      vsync: this,
    );

    _animation = Tween<double>(
      begin: 0.0,
      end: widget.progress,
    ).animate(CurvedAnimation(
      parent: _controller,
      curve: Curves.easeInOutCubic,
    ));

    _controller.forward();
  }

  @override
  void didUpdateWidget(AnimatedProgress oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.progress != widget.progress) {
      _animation = Tween<double>(
        begin: _controller.value,
        end: widget.progress,
      ).animate(CurvedAnimation(
        parent: _controller,
        curve: Curves.easeInOutCubic,
      ));
      _controller.forward(from: _controller.value);
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _animation,
      builder: (context, child) {
        return CustomPaint(
          painter: ProgressPainter(_animation.value, widget.color),
          child: child,
        );
      },
      child: Container(),
    );
  }
}

class ProgressPainter extends CustomPainter {
  final double progress;
  final Color color;

  ProgressPainter(this.progress, this.color);

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color.withOpacity(0.3)
      ..style = PaintingStyle.fill;

    // Background
    canvas.drawRRect(
      RRect.fromRectAndRadius(
        Rect.fromLTWH(0, 0, size.width, size.height),
        Radius.circular(size.height / 2),
      ),
      paint,
    );

    // Progress
    paint.color = color;
    canvas.drawRRect(
      RRect.fromRectAndRadius(
        Rect.fromLTWH(0, 0, size.width * progress, size.height),
        Radius.circular(size.height / 2),
      ),
      paint,
    );
  }

  @override
  bool shouldRepaint(ProgressPainter oldDelegate) {
    return oldDelegate.progress != progress || oldDelegate.color != color;
  }
}
```

### 2. Staggered Animation
Sequential animations with delays.

```dart
class StaggeredAnimationDemo extends StatefulWidget {
  final List<Widget> children;

  const StaggeredAnimationDemo({required this.children});

  @override
  _StaggeredAnimationDemoState createState() => _StaggeredAnimationDemoState();
}

class _StaggeredAnimationDemoState extends State<AnimatedListDemo>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late List<Animation<double>> _animations;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: Duration(milliseconds: 1200),
      vsync: this,
    );

    _animations = List.generate(
      widget.children.length,
      (index) => Tween<double>(
        begin: 0.0,
        end: 1.0,
      ).animate(CurvedAnimation(
        parent: _controller,
        curve: Interval(
          index * 0.1, // Start delay
          0.5 + (index * 0.1), // End delay
          curve: Curves.easeOutCubic,
        ),
      )),
    );

    _controller.forward();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: List.generate(
        widget.children.length,
        (index) => AnimatedBuilder(
          animation: _animations[index],
          builder: (context, child) {
            return Transform.translate(
              offset: Offset(0, 50 * (1 - _animations[index].value)),
              child: Opacity(
                opacity: _animations[index].value,
                child: child,
              ),
            );
          },
          child: widget.children[index],
        ),
      ),
    );
  }
}
```

## Physics Animations
Realistic motion with physics simulation.

### 1. Spring Animation
Bouncy, springy effects.

```dart
class SpringButton extends StatefulWidget {
  final Widget child;
  final VoidCallback onPressed;

  const SpringButton({required this.child, required this.onPressed});

  @override
  _SpringButtonState createState() => _SpringButtonState();
}

class _SpringButtonState extends State<SpringButton>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _scaleAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: Duration(milliseconds: 500),
      vsync: this,
    );

    _scaleAnimation = Tween<double>(
      begin: 1.0,
      end: 0.95,
    ).animate(CurvedAnimation(
      parent: _controller,
      curve: Curves.elasticIn,
    ));
  }

  void _handleTap() {
    _controller.forward().then((_) {
      _controller.reverse();
    });
    widget.onPressed();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: _handleTap,
      child: AnimatedBuilder(
        animation: _scaleAnimation,
        builder: (context, child) {
          return Transform.scale(
            scale: _scaleAnimation.value,
            child: child,
          );
        },
        child: widget.child,
      ),
    );
  }
}
```

### 2. Draggable Card
Physics-based dragging.

```dart
class DraggableCard extends StatefulWidget {
  final Widget child;
  final VoidCallback? onSwipeComplete;

  const DraggableCard({required this.child, this.onSwipeComplete});

  @override
  _DraggableCardState createState() => _DraggableCardState();
}

class _DraggableCardState extends State<DraggableCard>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<Offset> _slideAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: Duration(milliseconds: 300),
      vsync: this,
    );

    _slideAnimation = Tween<Offset>(
      begin: Offset.zero,
      end: Offset(1.5, 0), // Swipe off screen
    ).animate(CurvedAnimation(
      parent: _controller,
      curve: Curves.easeOutCubic,
    ));
  }

  void _handlePanUpdate(DragUpdateDetails details) {
    // Handle drag update
  }

  void _handlePanEnd(DragEndDetails details) {
    if (details.velocity.pixelsPerSecond.dx > 300) {
      // Swipe right
      _controller.forward().then((_) {
        widget.onSwipeComplete?.call();
      });
    } else {
      // Snap back
      _controller.reverse();
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onPanUpdate: _handlePanUpdate,
      onPanEnd: _handlePanEnd,
      child: AnimatedBuilder(
        animation: _slideAnimation,
        builder: (context, child) {
          return SlideTransition(
            position: _slideAnimation,
            child: child,
          );
        },
        child: widget.child,
      ),
    );
  }
}
```

## Hero Animations
Screen transitions with shared elements.

### 1. Hero Navigation
Smooth transitions between screens.

```dart
// First screen
class ProductListScreen extends StatelessWidget {
  final List<Product> products;

  const ProductListScreen({required this.products});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Products')),
      body: ListView.builder(
        itemCount: products.length,
        itemBuilder: (context, index) {
          final product = products[index];
          return GestureDetector(
            onTap: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => ProductDetailScreen(product: product),
                ),
              );
            },
            child: Hero(
              tag: 'product_${product.id}',
              child: ProductCard(product: product),
            ),
          );
        },
      ),
    );
  }
}

// Second screen
class ProductDetailScreen extends StatelessWidget {
  final Product product;

  const ProductDetailScreen({required this.product});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: CustomScrollView(
        slivers: [
          SliverAppBar(
            expandedHeight: 300,
            flexibleSpace: FlexibleSpaceBar(
              background: Hero(
                tag: 'product_${product.id}',
                child: Image.network(
                  product.imageUrl,
                  fit: BoxFit.cover,
                ),
              ),
            ),
          ),
          SliverToBoxAdapter(
            child: Padding(
              padding: EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    product.name,
                    style: Theme.of(context).textTheme.headlineMedium,
                  ),
                  SizedBox(height: 8),
                  Text(product.description),
                  // ... more content
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
```

### 2. Custom Hero Animation
Custom transition effects.

```dart
class CustomHero extends StatefulWidget {
  final Widget child;
  final String tag;
  final Duration duration;

  const CustomHero({
    required this.child,
    required this.tag,
    this.duration = const Duration(milliseconds: 600),
  });

  @override
  _CustomHeroState createState() => _CustomHeroState();
}

class _CustomHeroState extends State<CustomHero>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _scaleAnimation;
  late Animation<double> _fadeAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: widget.duration,
      vsync: this,
    );

    _scaleAnimation = Tween<double>(
      begin: 0.8,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _controller,
      curve: Curves.elasticOut,
    ));

    _fadeAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _controller,
      curve: Interval(0.3, 1.0, curve: Curves.easeOut),
    ));

    _controller.forward();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _controller,
      builder: (context, child) {
        return Transform.scale(
          scale: _scaleAnimation.value,
          child: Opacity(
            opacity: _fadeAnimation.value,
            child: child,
          ),
        );
      },
      child: widget.child,
    );
  }
}
```

## Performance Tips

### 1. Optimized Animations
Keep animations at 60fps.

```dart
class OptimizedAnimation extends StatefulWidget {
  @override
  _OptimizedAnimationState createState() => _OptimizedAnimationState();
}

class _OptimizedAnimationState extends State<OptimizedAnimation>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  Widget build(BuildContext context) {
    return RepaintBoundary( // Isolate repaints
      child: AnimatedBuilder(
        animation: _controller,
        builder: (context, child) {
          // Only rebuild what's necessary
          return Transform.rotate(
            angle: _controller.value * 2 * math.pi,
            child: child, // Pass child to avoid rebuilding
          );
        },
        child: const Icon(Icons.refresh), // const widget
      ),
    );
  }
}
```

### 2. Animation Curves
Choose appropriate easing functions.

```dart
// Common curves and their use cases
final curves = {
  'ease': Curves.ease, // Gentle acceleration and deceleration
  'easeIn': Curves.easeIn, // Slow start, fast end
  'easeOut': Curves.easeOut, // Fast start, slow end
  'easeInOut': Curves.easeInOut, // Slow start and end, fast middle
  'bounceIn': Curves.bounceIn, // Bouncy entrance
  'elasticOut': Curves.elasticOut, // Elastic exit
  'fastOutSlowIn': Curves.fastOutSlowIn, // Material design
};