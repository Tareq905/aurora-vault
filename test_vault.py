import aurora_vault

def main():
    vault = aurora_vault.load()

    query = "What is the Iliad?"
    print(f"\nSearching for: '{query}'...")

    results = vault.search(query, top_k=3)

    print("\n--- RESULTS ---")
    if not results:
        print("No matches found.")
    else:
        for i, r in enumerate(results, 1):
            print(f"{i}. {r['text']}\n")

if __name__ == "__main__":
    main()