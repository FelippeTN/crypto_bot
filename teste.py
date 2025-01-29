from tools.fetch_crypto import *

if __name__ == "__main__":
    
    file_path = os.path.join(os.getcwd(), "ativos.txt")

    try:
        with open(file_path, "r") as file:
            crypto_assets = [line.strip() for line in file.readlines()]
    except FileNotFoundError:
        crypto_assets = ["BTC-USD", "ETH-USD"]

    recommendations = rank_assets_with_qwen(crypto_assets)
    display_recommendations(recommendations)
    save_recommendations_to_files(recommendations)