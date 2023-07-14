import 'dart:typed_data';

abstract interface class Service {
  Future<Uint8List> submit({
    required Uint8List content,
    required Uint8List style,
    required int width,
    required int height,
    required int epochs,
    required double contentWeight,
    required double tvWeight,
    required double styleWeight,
  });
}
