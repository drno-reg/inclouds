**InClouds**

Система внешнего мониторинга
Версия 0.1

Про Pipeline: 
Изначально строился через hub.docker, НО с ним бывают проблемы.
Пришлось построить передачу свежих images через файлы.
Для этих целей создается каталог: /opt/docker/images и на него выдаются права 777.

Версия 0.1
Сделал оптимизцию распределения слоев в Docker контейнерах: объединил install в общие RUN и т.д.
