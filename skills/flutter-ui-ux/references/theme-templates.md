# Flutter Theme Templates

## Material Design 3 Themes
Modern Material You implementation.

### 1. Dynamic Color Theme
Adaptive colors based on system preferences.

```dart
class AppTheme {
  static ThemeData lightTheme(ColorScheme? dynamicColorScheme) {
    final colorScheme = dynamicColorScheme ??
      ColorScheme.fromSeed(
        seedColor: Colors.blue,
        brightness: Brightness.light,
      );

    return ThemeData(
      useMaterial3: true,
      colorScheme: colorScheme,
      brightness: Brightness.light,

      // Typography
      textTheme: _buildTextTheme(colorScheme),

      // Component themes
      elevatedButtonTheme: _elevatedButtonTheme(colorScheme),
      cardTheme: _cardTheme(colorScheme),
      appBarTheme: _appBarTheme(colorScheme),
      bottomNavigationBarTheme: _bottomNavTheme(colorScheme),
    );
  }

  static ThemeData darkTheme(ColorScheme? dynamicColorScheme) {
    final colorScheme = dynamicColorScheme ??
      ColorScheme.fromSeed(
        seedColor: Colors.blue,
        brightness: Brightness.dark,
      );

    return ThemeData(
      useMaterial3: true,
      colorScheme: colorScheme,
      brightness: Brightness.dark,

      textTheme: _buildTextTheme(colorScheme),
      elevatedButtonTheme: _elevatedButtonTheme(colorScheme),
      cardTheme: _cardTheme(colorScheme),
      appBarTheme: _appBarTheme(colorScheme),
      bottomNavigationBarTheme: _bottomNavTheme(colorScheme),
    );
  }

  static TextTheme _buildTextTheme(ColorScheme colorScheme) {
    return TextTheme(
      displayLarge: TextStyle(
        fontSize: 57,
        fontWeight: FontWeight.w400,
        color: colorScheme.onSurface,
      ),
      displayMedium: TextStyle(
        fontSize: 45,
        fontWeight: FontWeight.w400,
        color: colorScheme.onSurface,
      ),
      headlineLarge: TextStyle(
        fontSize: 32,
        fontWeight: FontWeight.w400,
        color: colorScheme.onSurface,
      ),
      headlineMedium: TextStyle(
        fontSize: 28,
        fontWeight: FontWeight.w400,
        color: colorScheme.onSurface,
      ),
      titleLarge: TextStyle(
        fontSize: 22,
        fontWeight: FontWeight.w500,
        color: colorScheme.onSurface,
      ),
      titleMedium: TextStyle(
        fontSize: 16,
        fontWeight: FontWeight.w500,
        color: colorScheme.onSurface,
      ),
      bodyLarge: TextStyle(
        fontSize: 16,
        fontWeight: FontWeight.w400,
        color: colorScheme.onSurface,
      ),
      bodyMedium: TextStyle(
        fontSize: 14,
        fontWeight: FontWeight.w400,
        color: colorScheme.onSurface,
      ),
      labelLarge: TextStyle(
        fontSize: 14,
        fontWeight: FontWeight.w500,
        color: colorScheme.onPrimary,
      ),
    );
  }

  static ElevatedButtonThemeData _elevatedButtonTheme(ColorScheme colorScheme) {
    return ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        backgroundColor: colorScheme.primary,
        foregroundColor: colorScheme.onPrimary,
        elevation: 2,
        padding: EdgeInsets.symmetric(horizontal: 24, vertical: 12),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20),
        ),
      ),
    );
  }

  static CardTheme _cardTheme(ColorScheme colorScheme) {
    return CardTheme(
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
      ),
      color: colorScheme.surface,
    );
  }

  static AppBarTheme _appBarTheme(ColorScheme colorScheme) {
    return AppBarTheme(
      backgroundColor: colorScheme.surface,
      foregroundColor: colorScheme.onSurface,
      elevation: 0,
      centerTitle: true,
      titleTextStyle: TextStyle(
        fontSize: 22,
        fontWeight: FontWeight.w500,
        color: colorScheme.onSurface,
      ),
    );
  }

  static BottomNavigationBarThemeData _bottomNavTheme(ColorScheme colorScheme) {
    return BottomNavigationBarThemeData(
      backgroundColor: colorScheme.surface,
      selectedItemColor: colorScheme.primary,
      unselectedItemColor: colorScheme.onSurfaceVariant,
      type: BottomNavigationBarType.fixed,
      elevation: 8,
      landscapeLayout: BottomNavigationBarLandscapeLayout.centered,
    );
  }
}
```

### 2. Brand Theme
Custom brand colors and styling.

```dart
class BrandTheme {
  // Brand colors
  static const Color primaryBrand = Color(0xFF2E7D32); // Green
  static const Color secondaryBrand = Color(0xFF1976D2); // Blue
  static const Color accentBrand = Color(0xFFFF6F00); // Orange

  static const Color lightBackground = Color(0xFFF5F5F5);
  static const Color darkBackground = Color(0xFF121212);

  static ThemeData lightBrandTheme() {
    final colorScheme = ColorScheme.fromSeed(
      seedColor: primaryBrand,
      brightness: Brightness.light,
      primary: primaryBrand,
      secondary: secondaryBrand,
      tertiary: accentBrand,
    );

    return ThemeData(
      useMaterial3: true,
      colorScheme: colorScheme,

      // Custom extensions
      extensions: [
        _BrandColors(
          primary: primaryBrand,
          secondary: secondaryBrand,
          accent: accentBrand,
          background: lightBackground,
        ),
      ],

      // Component themes
      elevatedButtonTheme: _brandElevatedButton(colorScheme),
      outlinedButtonTheme: _brandOutlinedButton(colorScheme),
      textButtonTheme: _brandTextButton(colorScheme),
      inputDecorationTheme: _brandInputDecoration(colorScheme),
    );
  }

  static ThemeData darkBrandTheme() {
    final colorScheme = ColorScheme.fromSeed(
      seedColor: primaryBrand,
      brightness: Brightness.dark,
      primary: primaryBrand,
      secondary: secondaryBrand,
      tertiary: accentBrand,
    );

    return ThemeData(
      useMaterial3: true,
      colorScheme: colorScheme,

      extensions: [
        _BrandColors(
          primary: primaryBrand,
          secondary: secondaryBrand,
          accent: accentBrand,
          background: darkBackground,
        ),
      ],

      elevatedButtonTheme: _brandElevatedButton(colorScheme),
      outlinedButtonTheme: _brandOutlinedButton(colorScheme),
      textButtonTheme: _brandTextButton(colorScheme),
      inputDecorationTheme: _brandInputDecoration(colorScheme),
    );
  }

  static ElevatedButtonThemeData _brandElevatedButton(ColorScheme colorScheme) {
    return ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        backgroundColor: primaryBrand,
        foregroundColor: Colors.white,
        elevation: 4,
        shadowColor: primaryBrand.withOpacity(0.3),
        padding: EdgeInsets.symmetric(horizontal: 32, vertical: 16),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
      ),
    );
  }

  static OutlinedButtonThemeData _brandOutlinedButton(ColorScheme colorScheme) {
    return OutlinedButtonThemeData(
      style: OutlinedButton.styleFrom(
        foregroundColor: primaryBrand,
        side: BorderSide(color: primaryBrand, width: 2),
        padding: EdgeInsets.symmetric(horizontal: 32, vertical: 16),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
      ),
    );
  }

  static TextButtonThemeData _brandTextButton(ColorScheme colorScheme) {
    return TextButtonThemeData(
      style: TextButton.styleFrom(
        foregroundColor: primaryBrand,
        padding: EdgeInsets.symmetric(horizontal: 24, vertical: 12),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(8),
        ),
      ),
    );
  }

  static InputDecorationTheme _brandInputDecoration(ColorScheme colorScheme) {
    return InputDecorationTheme(
      filled: true,
      fillColor: colorScheme.surface,
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: BorderSide(color: colorScheme.outline),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: BorderSide(color: primaryBrand, width: 2),
      ),
      errorBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: BorderSide(color: colorScheme.error, width: 2),
      ),
      contentPadding: EdgeInsets.symmetric(horizontal: 16, vertical: 12),
    );
  }
}

// Custom theme extension
@immutable
class _BrandColors extends ThemeExtension<_BrandColors> {
  final Color primary;
  final Color secondary;
  final Color accent;
  final Color background;

  const _BrandColors({
    required this.primary,
    required this.secondary,
    required this.accent,
    required this.background,
  });

  @override
  _BrandColors copyWith({
    Color? primary,
    Color? secondary,
    Color? accent,
    Color? background,
  }) {
    return _BrandColors(
      primary: primary ?? this.primary,
      secondary: secondary ?? this.secondary,
      accent: accent ?? this.accent,
      background: background ?? this.background,
    );
  }

  @override
  _BrandColors lerp(ThemeExtension<_BrandColors>? other, double t) {
    if (other is! _BrandColors) return this;

    return _BrandColors(
      primary: Color.lerp(primary, other.primary, t)!,
      secondary: Color.lerp(secondary, other.secondary, t)!,
      accent: Color.lerp(accent, other.accent, t)!,
      background: Color.lerp(background, other.background, t)!,
    );
  }
}
```

## Custom Theme System
Advanced theming with multiple variations.

### 1. Multi-Theme System
Switch between different visual themes.

```dart
enum AppThemeType { light, dark, blue, green, purple }

class ThemeManager extends ChangeNotifier {
  AppThemeType _currentTheme = AppThemeType.light;
  ThemeMode _themeMode = ThemeMode.system;

  AppThemeType get currentTheme => _currentTheme;
  ThemeMode get themeMode => _themeMode;

  void setTheme(AppThemeType theme) {
    _currentTheme = theme;
    notifyListeners();
  }

  void setThemeMode(ThemeMode mode) {
    _themeMode = mode;
    notifyListeners();
  }

  ThemeData get lightTheme => _getThemeData(AppThemeType.light, Brightness.light);
  ThemeData get darkTheme => _getThemeData(AppThemeType.dark, Brightness.dark);

  ThemeData _getThemeData(AppThemeType themeType, Brightness brightness) {
    switch (themeType) {
      case AppThemeType.light:
        return _buildLightTheme(brightness);
      case AppThemeType.dark:
        return _buildDarkTheme(brightness);
      case AppThemeType.blue:
        return _buildBlueTheme(brightness);
      case AppThemeType.green:
        return _buildGreenTheme(brightness);
      case AppThemeType.purple:
        return _buildPurpleTheme(brightness);
    }
  }

  ThemeData _buildLightTheme(Brightness brightness) {
    final colorScheme = ColorScheme.fromSeed(
      seedColor: Colors.blue,
      brightness: brightness,
    );

    return ThemeData(
      useMaterial3: true,
      colorScheme: colorScheme,
      appBarTheme: AppBarTheme(
        backgroundColor: colorScheme.surface,
        elevation: 0,
      ),
    );
  }

  ThemeData _buildBlueTheme(Brightness brightness) {
    final colorScheme = ColorScheme.fromSeed(
      seedColor: Colors.blue,
      brightness: brightness,
    );

    return ThemeData(
      useMaterial3: true,
      colorScheme: colorScheme,
      appBarTheme: AppBarTheme(
        backgroundColor: colorScheme.primaryContainer,
        foregroundColor: colorScheme.onPrimaryContainer,
      ),
    );
  }

  ThemeData _buildGreenTheme(Brightness brightness) {
    final colorScheme = ColorScheme.fromSeed(
      seedColor: Colors.green,
      brightness: brightness,
    );

    return ThemeData(
      useMaterial3: true,
      colorScheme: colorScheme,
      appBarTheme: AppBarTheme(
        backgroundColor: colorScheme.primary,
        foregroundColor: colorScheme.onPrimary,
      ),
    );
  }

  ThemeData _buildPurpleTheme(Brightness brightness) {
    final colorScheme = ColorScheme.fromSeed(
      seedColor: Colors.purple,
      brightness: brightness,
    );

    return ThemeData(
      useMaterial3: true,
      colorScheme: colorScheme,
      appBarTheme: AppBarTheme(
        backgroundColor: colorScheme.surfaceVariant,
        foregroundColor: colorScheme.onSurfaceVariant,
      ),
    );
  }
}

// Usage with Provider
class ThemeProvider extends StatelessWidget {
  final Widget child;

  const ThemeProvider({required this.child});

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (_) => ThemeManager(),
      child: Consumer<ThemeManager>(
        builder: (context, themeManager, child) {
          return MaterialApp(
            theme: themeManager.lightTheme,
            darkTheme: themeManager.darkTheme,
            themeMode: themeManager.themeMode,
            child: child!,
          );
        },
        child: child,
      ),
    );
  }
}
```

### 2. Theme Switcher Widget
UI for switching themes.

```dart
class ThemeSwitcher extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Consumer<ThemeManager>(
      builder: (context, themeManager, child) {
        return PopupMenuButton<AppThemeType>(
          icon: Icon(Icons.palette),
          onSelected: (theme) => themeManager.setTheme(theme),
          itemBuilder: (context) => [
            PopupMenuItem(
              value: AppThemeType.light,
              child: Row(
                children: [
                  Icon(Icons.light_mode, color: Colors.amber),
                  SizedBox(width: 8),
                  Text('Light'),
                ],
              ),
            ),
            PopupMenuItem(
              value: AppThemeType.dark,
              child: Row(
                children: [
                  Icon(Icons.dark_mode, color: Colors.blueGrey),
                  SizedBox(width: 8),
                  Text('Dark'),
                ],
              ),
            ),
            PopupMenuItem(
              value: AppThemeType.blue,
              child: Row(
                children: [
                  Icon(Icons.circle, color: Colors.blue),
                  SizedBox(width: 8),
                  Text('Blue'),
                ],
              ),
            ),
            PopupMenuItem(
              value: AppThemeType.green,
              child: Row(
                children: [
                  Icon(Icons.circle, color: Colors.green),
                  SizedBox(width: 8),
                  Text('Green'),
                ],
              ),
            ),
            PopupMenuItem(
              value: AppThemeType.purple,
              child: Row(
                children: [
                  Icon(Icons.circle, color: Colors.purple),
                  SizedBox(width: 8),
                  Text('Purple'),
                ],
              ),
            ),
          ],
        );
      },
    );
  }
}
```

## Responsive Theme Adaptation
Adapt themes for different screen sizes.

### 1. Responsive Theme Builder
Different themes for different screen sizes.

```dart
class ResponsiveTheme extends StatelessWidget {
  final Widget child;

  const ResponsiveTheme({required this.child});

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        ThemeData theme;

        if (constraints.maxWidth < 600) {
          // Mobile theme
          theme = _buildMobileTheme();
        } else if (constraints.maxWidth < 1200) {
          // Tablet theme
          theme = _buildTabletTheme();
        } else {
          // Desktop theme
          theme = _buildDesktopTheme();
        }

        return Theme(
          data: theme,
          child: child,
        );
      },
    );
  }

  ThemeData _buildMobileTheme() {
    return ThemeData(
      useMaterial3: true,
      textTheme: TextTheme(
        headlineLarge: TextStyle(fontSize: 24), // Smaller for mobile
        bodyLarge: TextStyle(fontSize: 16),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          padding: EdgeInsets.symmetric(horizontal: 16, vertical: 8), // Compact
        ),
      ),
    );
  }

  ThemeData _buildTabletTheme() {
    return ThemeData(
      useMaterial3: true,
      textTheme: TextTheme(
        headlineLarge: TextStyle(fontSize: 32), // Medium
        bodyLarge: TextStyle(fontSize: 18),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          padding: EdgeInsets.symmetric(horizontal: 24, vertical: 12),
        ),
      ),
    );
  }

  ThemeData _buildDesktopTheme() {
    return ThemeData(
      useMaterial3: true,
      textTheme: TextTheme(
        headlineLarge: TextStyle(fontSize: 40), // Larger for desktop
        bodyLarge: TextStyle(fontSize: 20),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          padding: EdgeInsets.symmetric(horizontal: 32, vertical: 16), // Spacious
        ),
      ),
    );
  }
}
```

## Theme Usage Examples

### 1. Access Theme in Widgets
Proper theme access patterns.

```dart
class ThemedWidget extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final textTheme = theme.textTheme;

    return Container(
      color: colorScheme.primary,
      child: Text(
        'Themed Text',
        style: textTheme.headlineMedium?.copyWith(
          color: colorScheme.onPrimary,
        ),
      ),
    );
  }
}

// Using custom theme extensions
class CustomThemedWidget extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final brandColors = Theme.of(context).extension<_BrandColors>();

    return Container(
      color: brandColors?.primary ?? Colors.blue,
      child: Text(
        'Brand Themed',
        style: TextStyle(color: brandColors != null ? Colors.white : null),
      ),
    );
  }
}
```

### 2. Theme Switching Animation
Smooth theme transitions.

```dart
class AnimatedThemeSwitch extends StatefulWidget {
  final Widget child;

  const AnimatedThemeSwitch({required this.child});

  @override
  _AnimatedThemeSwitchState createState() => _AnimatedThemeSwitchState();
}

class _AnimatedThemeSwitchState extends State<AnimatedThemeSwitch>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _animation;

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

  void switchTheme(ThemeData newTheme) {
    _controller.forward().then((_) {
      // Update theme
      _controller.reverse();
    });
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
        return Opacity(
          opacity: 1.0 - _animation.value.abs() * 0.3,
          child: child,
        );
      },
      child: widget.child,
    );
  }
}