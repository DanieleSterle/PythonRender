# Daniele Sterle SM3201594

import numpy as np

# Eccezione personalizzata per errori di caricamento e decodifica della VRAM virtuale.
class VirtualVRAMException(Exception):
    pass

class VirtualVRAM():

    # Carica e decodifica sia il foglio dei tile che quello degli sprite.
    def __init__(self, tiles_path, sprites_path):
        self.tiles = self.__load_and_decode_sheet(tiles_path, 256, 32, 8, 8)
        self.sprites = self.__load_and_decode_sheet(sprites_path, 256, 64, 4, 4)

    # Funzione di supporto che gestisce sequenzialmente caricamento, decodifica e suddivisione in griglia.
    def __load_and_decode_sheet(self, filepath, sheet_size, item_size, grid_rows, grid_cols):
        raw_data = self.__load(filepath, sheet_size)
        sheet_2d = self.__decode(raw_data, sheet_size)
        return self.__split_into_grid(sheet_2d, grid_rows, grid_cols, item_size)

    # Carica e valida i dati grezzi del file binario.
    def __load(self, filepath, sheet_size):
        try:
            with open(filepath, "rb") as file:
                raw_data = file.read()
        except Exception as e:
            raise VirtualVRAMException(f"Failed to read binary file {filepath}: {e}")

        expected_bytes = (sheet_size * sheet_size) // 2  # 32768 bytes

        if len(raw_data) != expected_bytes:
            raise VirtualVRAMException(f"Invalid file size for {filepath}. Expected {expected_bytes} bytes.")

        return raw_data

    # Decodifica i nibble a 4 bit impacchettati in una matrice 2D di indici di palette.
    def __decode(self, raw_data, sheet_size):
        # Converte i byte grezzi in un array numpy di interi a 8 bit senza segno
        byte_array = np.frombuffer(raw_data, dtype = np.uint8)

        # Estrazione dei nibble: ogni byte della VRAM memorizza 2 pixel impacchettati 
        # (ciascun pixel occupa 4 bit: il nibble alto nei primi 4 bit, quello basso negli ultimi 4).
        # Per isolare il nibble alto, spostiamo i bit a destra di 4 posizioni (>>).
        # In questo modo i 4 bit più a destra vengono scartati e i 4 bit di sinistra 
        # si spostano nella parte destra del byte.
        high_nibble = byte_array >> 4

        # Per isolare il nibble basso, utilizziamo una maschera bit-wise AND (&) con 0x0F (0000 1111 in binario).
        # La maschera azzera completamente i primi 4 bit a sinistra e preserva 
        # intatti gli ultimi 4 bit a destra, che rappresentano il secondo pixel del byte.
        low_nibble = byte_array & 0x0F

        # Unisce i pixel del nibble alto e basso in un unico array alternandoli nell'ordine corretto
        pixels = np.empty(sheet_size * sheet_size, dtype = np.uint8)
        pixels[0::2] = high_nibble
        pixels[1::2] = low_nibble

        # Ridisegna l'array monodimensionale in una matrice 2D (sheet_size x sheet_size)
        return pixels.reshape((sheet_size, sheet_size))

    # Suddivide la matrice 2D del foglio nei singoli elementi della griglia (tile o sprite).
    def __split_into_grid(self, sheet_2d, grid_rows, grid_cols, item_size):
        items = []
        for r in range(grid_rows):
            for c in range(grid_cols):
                # Calcola le coordinate verticali (inizio, fine)
                y1 = r * item_size
                y2 = y1 + item_size

                # Calcola le coordinate orizzontali (inizio, fine)
                x1 = c * item_size
                x2 = x1 + item_size

                # Estrae il singolo elemento (tile o sprite) tramite slicing della matrice
                item = sheet_2d[y1:y2, x1:x2]
                items.append(item)

        # Restituisce tutti gli elementi come un unico array numpy
        return np.array(items, dtype = np.uint8)