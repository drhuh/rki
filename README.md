# Aufruf

## Daten holen und absolute Infektionen anzeigen

```
./evaluate_rki_numbers.py -i ~/Downloads/RKI_COVID19.csv -f
```

## Sterbefälle absolut

```
./evaluate_rki_numbers.py -i RKI_COVID19.csv -m
```

## Sterbefälle relativ bezogen auf die Einwohner pro Bundesland

```
./evaluate_rki_numbers.py -i RKI_COVID19.csv -m -p bundeslaender.csv
```

