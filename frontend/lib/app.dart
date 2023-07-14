import 'package:style_transfer/home_model.dart';
import 'package:style_transfer/service.dart';
import 'package:style_transfer/style_service.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import 'home_page.dart';

class ContentStylerApp extends StatelessWidget {
  const ContentStylerApp({super.key});

  @override
  Widget build(BuildContext context) {
    Service service = StyleService();

    return MaterialApp(
      title: 'Style Transfer',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
        useMaterial3: true,
      ),
      home: ChangeNotifierProvider<HomeModel>(
        create: (BuildContext context) => HomeModel(service),
        child: HomePage(),
      ),
    );
  }
}
