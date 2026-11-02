"""Pequenos utilitários de saída narrada (PT-BR) e de linha de comando."""
import argparse


def ler_argumentos(descricao, argv=None):
    ap = argparse.ArgumentParser(description=descricao,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--defesa", action="store_true",
                    help="liga as defesas ao redor do modelo (padrão: desligadas = versão vulnerável)")
    return ap.parse_args(argv)


def cabecalho(titulo, defesa):
    modo = "COM DEFESA" if defesa else "SEM DEFESA (versão vulnerável)"
    print("=" * 74)
    print(titulo)
    print("Modo: " + modo)
    print("Aviso: SimLLM é um SIMULADOR didático, não um modelo real. Uso educacional.")
    print("=" * 74)


def secao(nome):
    print("\n--- " + nome + " ---")


def linha(texto="", indent=2):
    for parte in str(texto).split("\n"):
        print(" " * indent + parte)
