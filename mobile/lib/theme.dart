import 'package:flutter/material.dart';

/// Matte black + gold Material 3 dark theme. No analytics.
const Color kMatteBlack = Color(0xFF0B0B0B);
const Color kSurface = Color(0xFF141414);
const Color kGold = Color(0xFFC9A227);
const Color kGoldDim = Color(0xFF8A7219);
const Color kIvory = Color(0xFFE8E0D0);

ThemeData _theme(ColorScheme scheme) {
  final dark = scheme.brightness == Brightness.dark;
  return ThemeData(
    useMaterial3: true,
    brightness: scheme.brightness,
    colorScheme: scheme,
    scaffoldBackgroundColor: dark ? kMatteBlack : const Color(0xFFF6F3EA),
    focusColor: kGold,
    appBarTheme: AppBarTheme(
      backgroundColor: dark ? kMatteBlack : const Color(0xFFF6F3EA),
      foregroundColor: dark ? kGold : const Color(0xFF1C1915),
      elevation: 0,
      centerTitle: false,
    ),
    cardTheme: CardThemeData(
      color: scheme.surface,
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: const BorderSide(color: Color(0x33C9A227)),
      ),
    ),
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: scheme.surface,
      border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(10),
        borderSide: const BorderSide(color: kGold, width: 2),
      ),
    ),
    segmentedButtonTheme: SegmentedButtonThemeData(
      style: ButtonStyle(
        foregroundColor: WidgetStateProperty.resolveWith((s) {
          return s.contains(WidgetState.selected) ? kMatteBlack : scheme.onSurface;
        }),
        backgroundColor: WidgetStateProperty.resolveWith((s) {
          return s.contains(WidgetState.selected) ? kGold : scheme.surface;
        }),
      ),
    ),
  );
}

ThemeData buildAppTheme() {
  const dark = ColorScheme.dark(
    brightness: Brightness.dark,
    primary: kGold,
    onPrimary: kMatteBlack,
    secondary: kGoldDim,
    onSecondary: kIvory,
    surface: kSurface,
    onSurface: kIvory,
    error: Color(0xFFB54A4A),
    onError: kIvory,
  );
  return _theme(dark);
}

ThemeData buildLightTheme() {
  const light = ColorScheme.light(
    brightness: Brightness.light,
    primary: kGold,
    onPrimary: Color(0xFF1A1408),
    secondary: kGoldDim,
    onSecondary: Color(0xFF1C1915),
    surface: Color(0xFFFFFCF6),
    onSurface: Color(0xFF1C1915),
    error: Color(0xFF8C1D18),
    onError: Color(0xFFFFFCF6),
  );
  return _theme(light);
}
