# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
#
# NOTE: In order to generate from Oracle DB, we had to use this hotfix:
# https://stackoverflow.com/questions/11832817/how-do-i-run-inspectdb-against-different-schemas-in-oracle
from django.db import models


class CPredmetyFei(models.Model):
    obdobie = models.CharField(max_length=100)
    id = models.BigIntegerField(primary_key=True)
    garantujuce_pracovisko = models.BigIntegerField()
    garant = models.BigIntegerField()
    kod = models.CharField(max_length=10)
    nazov = models.CharField(max_length=500, blank=True, null=True)
    nazov_ang = models.CharField(max_length=500, blank=True, null=True)
    std_ukonc = models.CharField(max_length=10, blank=True, null=True)
    kredity = models.CharField(max_length=1500)

    class Meta:
        managed = False
        db_table = u'"PRENOS"."C_PREDMETY_FEI"'


class AISObdobia(models.Model):
    id = models.BigIntegerField(primary_key=True)
    pracovisko = models.IntegerField(null=False)
    aktivne = models.BooleanField(null=True, default=None)
    zaciatok = models.DateField(null=True, default=None)
    koniec = models.DateField(null=True, default=None)
    nasledujuce = models.IntegerField(null=True, default=None)
    predchadzajuce = models.IntegerField(null=True, default=None)
    por_ar = models.IntegerField(null=False)
    univ_obdobie = models.IntegerField(null=False)
    pracovisko = models.IntegerField(null=False)
    nazov_ang = models.CharField(max_length=100, null=False)
    nazov_sk = models.CharField(max_length=100, null=False)

    class Meta:
        managed = False
        db_table = u'"PRENOS"."AIS_OBDOBIA"'


class FeiDepartments(models.Model):
    id = models.BigIntegerField(primary_key=True)
    skratka = models.CharField(max_length=20, blank=True, null=True)
    nazov = models.CharField(max_length=1000, blank=True, null=True)
    nadriadene_prac = models.CharField(max_length=40, blank=True, null=True)

    class Meta:
        managed = False
        db_table = u'"PRENOS"."FEI_DEPARTMENTS"'


class FeiEquipments(models.Model):
    id = models.BigIntegerField(primary_key=True)
    nazov = models.CharField(max_length=1000, blank=True, null=True)

    class Meta:
        managed = False
        db_table = u'"PRENOS"."FEI_EQUIPMENTS"'


class FeiGroups(models.Model):
    id = models.BigIntegerField(primary_key=True)
    nazov = models.CharField(max_length=1500, blank=True, null=True)
    skratka = models.CharField(max_length=1601, blank=True, null=True)
    nadriadena_skupina = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = u'"PRENOS"."FEI_GROUPS"'


class FeiRooms(models.Model):
    id = models.BigIntegerField(primary_key=True)
    nazov = models.CharField(max_length=20)
    kapacita = models.BigIntegerField(blank=True, null=True)
    typ = models.BigIntegerField(blank=True, null=True)
    pracovisko = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = u'"PRENOS"."FEI_ROOMS"'


class FeiRoomsEquipments(models.Model):
    miestnost = models.BigIntegerField(primary_key=True)
    pomocka = models.BigIntegerField()
    pocet = models.CharField(max_length=1500)

    class Meta:
        managed = False
        db_table = u'"PRENOS"."FEI_ROOMS_EQUIPMENTS"'


class FeiRoomtypes(models.Model):
    id = models.BigIntegerField(primary_key=True)
    nazov = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = u'"PRENOS"."FEI_ROOMTYPES"'


class FeiSubjects(models.Model):
    obdobie = models.CharField(max_length=100, blank=True, null=True)
    id = models.BigIntegerField(blank=True, primary_key=True)
    kod = models.CharField(max_length=10, blank=True, null=True)
    nazov = models.CharField(max_length=500, blank=True, null=True)
    pracovisko = models.BigIntegerField(blank=True, null=True)
    std_ukonc = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = u'"PRENOS"."FEI_SUBJECTS"'


class FeiSubjectsUsers(models.Model):
    predmet = models.BigIntegerField(blank=True, null=True)
    ais_id = models.BigIntegerField(blank=True, primary_key=True)
    rola = models.CharField(max_length=40, blank=True, null=True)

    class Meta:
        managed = False
        db_table = u'"PRENOS"."FEI_SUBJECTS_USERS"'


class FeiUsers(models.Model):
    ais_id = models.BigIntegerField(blank=True, primary_key=True)
    login = models.CharField(max_length=20, blank=True, null=True)
    meno = models.CharField(max_length=50, blank=True, null=True)
    priezvisko = models.CharField(max_length=70, blank=True, null=True)
    tituly_pred = models.CharField(max_length=300, blank=True, null=True)
    tituly_za = models.CharField(max_length=300, blank=True, null=True)
    karta = models.CharField(max_length=32767, blank=True, null=True)

    class Meta:
        managed = False
        db_table = u'"PRENOS"."FEI_USERS"'


class FeiUsersDepartments(models.Model):
    ais_id = models.BigIntegerField(blank=True, primary_key=True)
    pracovisko = models.FloatField(blank=True, null=True)
    typ_pracovneho_pomeru = models.CharField(max_length=9, blank=True, null=True)

    class Meta:
        managed = False
        db_table = u'"PRENOS"."FEI_USERS_DEPARTMENTS"'


class FeiUsersGroups(models.Model):
    ais_id = models.BigIntegerField(primary_key=True)
    skupina = models.IntegerField(blank=True, null=True)
    kruzok = models.CharField(max_length=1500, blank=True, null=True)
    forma = models.CharField(max_length=7, blank=True, null=True)
    metoda = models.CharField(max_length=11, blank=True, null=True)

    class Meta:
        managed = False
        db_table = u'"PRENOS"."FEI_USERS_GROUPS"'
