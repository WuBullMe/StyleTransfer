import 'dart:math';

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
  double contentWeight = 0;
  double tvWeight = 0;
  double styleWeight = 0;

  HomeModel(Service service) : _service = service;

  Uint8List? get content => _content;

  Uint8List? get style => _style;

  Uint8List? get result => _result;

  set content(Uint8List? bytes) {
    _content = bytes;
    notifyListeners();
  }

  set style(Uint8List? bytes) {
    _style = bytes;
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
    _result = await _service.submit(
      content: _content!,
      style: _style!,
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
}
