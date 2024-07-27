--
-- Файл сгенерирован с помощью SQLiteStudio v3.4.4 в Вс июл 28 01:02:43 2024
--
-- Использованная кодировка текста: System
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Таблица: main_card
CREATE TABLE IF NOT EXISTS "main_card" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "title" varchar(50) NOT NULL, "slug" varchar(255) NOT NULL UNIQUE, "description" text NOT NULL);
INSERT INTO main_card (id, title, slug, description) VALUES (2, 'ТСН "ЗВЕЗДНЫЙ-7"', 'tsn-zvezdnyj-7', '<p>Адрес: Саратовская обл. Энгельсский рн, рп Приволжский,<br />
ул. Гагарина дом 7</p>

<p>Телефон:&nbsp;<a href="tel:+79271438852">+79271438852</a></p>

<p>Адрес электронной почты:&nbsp;<a href="mailto:tsnzv@yandex.ru">tsnzv@yandex.ru</a></p>

<p>Контактные телефоны АДС:</p>

<p>&nbsp;<a href="tel:+78453611374,+79271438852">+79271438852</a></p>');
INSERT INTO main_card (id, title, slug, description) VALUES (3, 'Режим работы', 'rezhim-raboty-i-priem-grazhdan', '<p>Понедельник - пятница&nbsp;</p>

<p>с 9:00 - 17:00</p>

<p>Обед 12:00 - 13:00</p>

<p>Суббота, воскресенье - выходной</p>

<p>Прием граждан осуществляется по адресу:</p>

<p>Саратовская обл. Энгельсский рн, рп Приволжский, ул. Гагарина дом 7</p>

<p>(с торца дома),</p>

<p>понедельник - пятница</p>

<p>c 9:00 - 17:00</p>');
INSERT INTO main_card (id, title, slug, description) VALUES (4, 'Мы находимся', 'my-nahodimsya', '<p><iframe frameborder="0" height="350" scrolling="no" src="https://yandex.ru/map-widget/v1/?um=constructor%3Acd4952e61ee78323ea9b94c9e3e3f989a0df433d22de34f89ad97658ada38068&amp;amp;source=constructor" width="100%"></iframe></p>');

-- Индекс: sqlite_autoindex_main_card_1
CREATE UNIQUE INDEX IF NOT EXISTS sqlite_autoindex_main_card_1 ON main_card (slug COLLATE BINARY);

COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
