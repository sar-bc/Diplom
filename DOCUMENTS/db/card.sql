--
-- ���� ������������ � ������� SQLiteStudio v3.4.4 � �� ��� 28 01:02:43 2024
--
-- �������������� ��������� ������: System
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- �������: main_card
CREATE TABLE IF NOT EXISTS "main_card" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "title" varchar(50) NOT NULL, "slug" varchar(255) NOT NULL UNIQUE, "description" text NOT NULL);
INSERT INTO main_card (id, title, slug, description) VALUES (2, '��� "��������-7"', 'tsn-zvezdnyj-7', '<p>�����: ����������� ���. ����������� ��, �� �����������,<br />
��. �������� ��� 7</p>

<p>�������:&nbsp;<a href="tel:+79271438852">+79271438852</a></p>

<p>����� ����������� �����:&nbsp;<a href="mailto:tsnzv@yandex.ru">tsnzv@yandex.ru</a></p>

<p>���������� �������� ���:</p>

<p>&nbsp;<a href="tel:+78453611374,+79271438852">+79271438852</a></p>');
INSERT INTO main_card (id, title, slug, description) VALUES (3, '����� ������', 'rezhim-raboty-i-priem-grazhdan', '<p>����������� - �������&nbsp;</p>

<p>� 9:00 - 17:00</p>

<p>���� 12:00 - 13:00</p>

<p>�������, ����������� - ��������</p>

<p>����� ������� �������������� �� ������:</p>

<p>����������� ���. ����������� ��, �� �����������, ��. �������� ��� 7</p>

<p>(� ����� ����),</p>

<p>����������� - �������</p>

<p>c 9:00 - 17:00</p>');
INSERT INTO main_card (id, title, slug, description) VALUES (4, '�� ���������', 'my-nahodimsya', '<p><iframe frameborder="0" height="350" scrolling="no" src="https://yandex.ru/map-widget/v1/?um=constructor%3Acd4952e61ee78323ea9b94c9e3e3f989a0df433d22de34f89ad97658ada38068&amp;amp;source=constructor" width="100%"></iframe></p>');

-- ������: sqlite_autoindex_main_card_1
CREATE UNIQUE INDEX IF NOT EXISTS sqlite_autoindex_main_card_1 ON main_card (slug COLLATE BINARY);

COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
