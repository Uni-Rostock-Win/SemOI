1. Image in Docker erstellen:
            docker build -t sema/webapp .
            
            
2. Image ausführen und den Port 8000 über den Port 8002 erreichen:
            docker run -p 8002:8000 sema/webapp
			
			
3. Aufrufbar unter http://127.0.0.1:8002


------------------------------------------------------------------------------
Kurze Erläuterung zum Code

- templates/upload.html ist Home Seite
- unter pages/views.py ist definiert wie bei einen Bildupload auf der Home Seite vorgegangen werden soll
- pages/tf_hub.py beinhaltet die komplette Tensorflow Engine
- pages/semanticCaller.py beinhaltet den kompletten Code um auf die Semantik API von Achim Reiz zuzugreifen
- oidv4_LabelMap.txt wird benötigt, um die erkannten Objekte in die ObjektID von OpenImage v4 umzuwandeln und diese an die SemantikAPI zu senden



