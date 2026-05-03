from __future__ import annotations

import argparse
import logging
import shutil
import time
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


FILE_CATEGORIES = {
    "Imagens": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp"},
    "Documentos": {".pdf", ".doc", ".docx", ".txt"},
    "Planilhas": {".xls", ".xlsx", ".csv"},
    "Apresentacoes": {".ppt", ".pptx"},
    "Compactados": {".zip", ".rar", ".7z", ".tar", ".gz"},
    "Midias": {".mp3", ".wav", ".mp4", ".mov", ".avi"},
    "Executaveis": {".exe", ".msi"},
}

RETRY_DELAY_SECONDS = 1
RETRY_ATTEMPTS = 5

"""Configura o formato e o nível das mensagens de Log exibidas no console."""
def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


"""Identifica a categoria de um arquivo com base em sua extensão. Se a extensão não for reconhecida, retorna 'Outros'."""
def resolve_category(file_path: Path) -> str:
    suffix = file_path.suffix.lower()

    for category, extensions in FILE_CATEGORIES.items():
        if suffix in extensions:
            return category

    return "Outros"


"""Garante que o arquivo seja movido para um destino único, evitando sobrescritas. Se um arquivo com o mesmo nome já existir, adiciona um sufixo numérico ao nome do arquivo."""
def unique_destination(destination: Path) -> Path:
    if not destination.exists():
        return destination

    stem = destination.stem
    suffix = destination.suffix
    counter = 1

    while True:
        candidate = destination.with_name(f"{stem}_{counter}{suffix}")
        if not candidate.exists():
            return candidate
        counter += 1


"""Move um arquivo para a pasta correspondente à sua categoria."""
def move_file(file_path: Path, destination_root: Path) -> None:
    if not file_path.exists() or not file_path.is_file():
        return

    category = resolve_category(file_path)
    target_dir = destination_root / category
    target_dir.mkdir(parents=True, exist_ok=True)

    destination = unique_destination(target_dir / file_path.name)
    shutil.move(str(file_path), str(destination))
    logging.info("Arquivo movido: %s -> %s", file_path.name, destination.parent.name)


"""Organiza os arquivos existentes na pasta de origem ao iniciar o programa."""
def organize_existing_files(source_dir: Path, destination_root: Path) -> None:
    for item in source_dir.iterdir():
        if item.is_file():
            move_with_retry(item, destination_root)


"""Tenta mover um arquivo algumas vezes caso ele esteja em uso."""
def move_with_retry(file_path: Path, destination_root: Path) -> None:
    for attempt in range(1, RETRY_ATTEMPTS + 1):
        try:
            move_file(file_path, destination_root)
            return
        except PermissionError:
            logging.warning(
                "Arquivo ainda em uso (%s). Nova tentativa %s/%s.",
                file_path.name,
                attempt,
                RETRY_ATTEMPTS,
            )
            time.sleep(RETRY_DELAY_SECONDS)
        except FileNotFoundError:
            return
        except shutil.Error as error:
            logging.error("Nao foi possivel mover %s: %s", file_path.name, error)
            return

    logging.error("Falha ao mover %s apos varias tentativas.", file_path.name)

"""Classe responsável por reagir a eventos da pasta monitorada."""
class FileOrganizerHandler(FileSystemEventHandler):

    """Recebe e armazena a pasta de destino dos arquivos organizados."""
    def __init__(self, destination_root: Path) -> None:
        super().__init__()
        self.destination_root = destination_root

    """Executa quando um novo arquivos é criado na pasta monitorada."""
    def on_created(self, event) -> None:  # type: ignore[override]
        if event.is_directory:
            return

        move_with_retry(Path(event.src_path), self.destination_root)

    """Executa quando um arquivo é movido para dentro da pasta monitorada."""
    def on_moved(self, event) -> None:  # type: ignore[override]
        if event.is_directory:
            return

        move_with_retry(Path(event.dest_path), self.destination_root)

"""Lê os argumentos enviados pelo terminal e retorna um objeto com as configurações para o programa."""
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Monitora uma pasta e organiza arquivos automaticamente por tipo."
    )
    parser.add_argument(
        "--source",
        default="entrada",
        help="Pasta monitorada pelo robo. Padrao: ./entrada",
    )
    parser.add_argument(
        "--destination",
        default=None,
        help="Pasta de destino. Se nao for informada, usa a propria pasta monitorada.",
    )
    return parser.parse_args()


"""Função principal do programa, responsável por configurar o ambiente, organizar os arquivos existentes e iniciar a monitoração da pasta."""
def main() -> None:
    args = parse_args()
    configure_logging()

    source_dir = Path(args.source).resolve()
    destination_root = Path(args.destination).resolve() if args.destination else source_dir

    source_dir.mkdir(parents=True, exist_ok=True)
    destination_root.mkdir(parents=True, exist_ok=True)

    logging.info("Monitorando pasta: %s", source_dir)
    logging.info("Destino da organizacao: %s", destination_root)

    organize_existing_files(source_dir, destination_root)

    event_handler = FileOrganizerHandler(destination_root)
    observer = Observer()
    observer.schedule(event_handler, str(source_dir), recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Encerrando robo de automacao.")
        observer.stop()

    observer.join()


if __name__ == "__main__":
    main()
