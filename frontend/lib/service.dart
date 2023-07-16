import 'dart:typed_data';

abstract interface class Service {
  Future<(Uint8List, (String, String))> submit({
    required Uint8List content,
    required Uint8List style,
    required int width,
    required int height,
    required int epochs,
    required double contentWeight,
    required double tvWeight,
    required double styleWeight,
  });

  Future<(Uint8List, (String, String))> submitLite({
    required int width,
    required int height,
    required int epochs,
    required double contentWeight,
    required double tvWeight,
    required double styleWeight,
    required (String, String) id,
  });
}
