import 'dart:async';
import 'dart:math' show min, max;

import 'package:image/image.dart';
import 'package:style_transfer/service.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/widgets.dart';

class HomeModel extends ChangeNotifier {
  final widthController = TextEditingController(text: '512');
  final heightController = TextEditingController(text: '512');
  final epochsController = TextEditingController(text: '100');
  final rangeController = TextEditingController(text: '1000');

  final Service _service;
  Uint8List? _content;
  Uint8List? _style;
  Uint8List? _result;
  int width = 512;
  int height = 512;
  int epochs = 100;
  int range = 1000;
  double contentWeight = 5e0;
  double tvWeight = 1e-5;
  double styleWeight = 2e2;

  HomeModel(Service service) : _service = service;

  Uint8List? get content => _content;

  Uint8List? get style => _style;

  Uint8List? get result => _result;

  void setContent(Uint8List? bytes, Function(int, int) onBigDimensions) {
    _content = bytes;
    if (bytes != null) {
      var (w, h) = _getImageSize(bytes);
      width = w;
      height = h;
      if (w > 1920 || h > 1080) {
        int F = max((w / 1920).ceil(), (h / 1080).ceil());
        width = (width / F).floor();
        height = (height / F).floor();
        _content = _resize(_content!, width, height);
        onBigDimensions(width, height);
      }
      widthController.text = width.toString();
      heightController.text = height.toString();
    }
    notifyListeners();
  }

  set style(Uint8List? bytes) {
    _style = bytes;
    if (bytes != null) {
      var (w, h) = _getImageSize(bytes);
      if (w > 1920 || h > 1080) {
        int F = max((w / 1920).ceil(), (h / 1080).ceil());
        _style = _resize(_style!, (w / F).floor(), (h / F).floor());
      }
      widthController.text = width.toString();
      heightController.text = height.toString();
    }
    notifyListeners();
  }

  void setRange(int r) {
    contentWeight = min(contentWeight, r.toDouble());
    tvWeight = min(tvWeight, r.toDouble());
    styleWeight = min(styleWeight, r.toDouble());
    range = r;
    notifyListeners();
  }

  Future<void> submit() async {
    var content = _resize(_content!, width, height);
    var style = _resize(_style!, width, height);
    _result = await _service.submit(
      content: content,
      style: style,
      width: width,
      height: height,
      epochs: epochs,
      contentWeight: contentWeight,
      tvWeight: tvWeight,
      styleWeight: styleWeight,
    );
    notifyListeners();
  }

  void save() {
    width = int.parse(widthController.text);
    height = int.parse(heightController.text);
    epochs = int.parse(epochsController.text);
    range = int.parse(rangeController.text);
  }

  (int, int) _getImageSize(Uint8List bytes) {
    var image = decodeImage(bytes);
    return (image!.width, image.height);
  }

  Uint8List _resize(Uint8List bytes, int newWidth, int newHeight) {
    var image = decodeImage(bytes);
    if (image != null) {
      var resized = copyResize(image, width: newWidth, height: newHeight);
      return encodePng(resized);
    }
    return bytes;
  }
}
