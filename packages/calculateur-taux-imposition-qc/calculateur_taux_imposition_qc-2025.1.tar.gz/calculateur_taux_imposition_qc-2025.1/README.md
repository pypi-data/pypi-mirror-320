# Calculateur de Taux d'Imposition QC

Ce projet est un calculateur de taux d'imposition aux particuliers pour la province de Québec, Canada. Il permet de calculer les impôts à payer en fonction des revenus obtenu lors d'une année. Le calculateur est présentement limité aux années 2023 à 2025.


## Utilisation

Pour utiliser le calculateur en ligne de commande, exécutez le script `calculateur.py` avec les arguments suivants :

```bash
python main.py <salaire_annuel> [annee]
```
Vous pouvez aussi installer comme une librairie pour l'utiliser plus facilement dans votre code:
```bash
python -m pip install .
```

### Arguments

- `salaire_annuel` : Le montant du salaire annuel brute pour lequel vous souhaitez calculer l'impôt.
- `annee` : L'année pour laquelle vous souhaitez effectuer le calcul (2023, 2024, ou 2025). L'argument est optionnel et sera l'année actuelle par défaut.

### Exemple

```bash
python calculateur.py 50000 2023
```
```bash
python calculateur.py 40000
```
Exemple de retour:
```JSON
{
    "taux_effectif_quebecois": 0.1587,
    "taux_effectif_canadien": 0.1679,
    "taux_effectif_total": 0.3265,
    "taux_marginal_quebecois": 0.19,
    "taux_marginal_canadien": 0.205,
    "taux_marginal_total": 0.395
}
```

## Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## Auteurs

- Samuel Paquette-Paré [paquetteparesamuel@gmail.com]
