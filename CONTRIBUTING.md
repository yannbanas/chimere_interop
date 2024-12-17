
#### CONTRIBUTING.md (extrait)

```markdown
# Guide de contribution

Nous encourageons la communauté à contribuer en ajoutant de nouveaux types de données, adaptateurs ou en améliorant la documentation.

## Ajouter un nouveau type

1. Créez une classe dans `chimere/types.py` héritant de `BaseRepresentation`.
2. Documentez ses attributs et son usage.
3. Ajoutez des tests unitaires dans `tests/`.

## Ajouter un nouvel adaptateur

1. Dans un nouveau fichier (ex: `chimere/adapters/my_adapter.py`) ou dans `adapters_example.py`, créez une classe implémentant une méthode `convert()`.
2. Décorez-la avec `@register_adapter(from_type=..., to_type=...)`.
3. Ajoutez des tests unitaires.
4. Soumettez une PR.

## Revue de code

Les PR seront examinées par la communauté. Suivez les conventions PEP8 et ajoutez des docstrings.
