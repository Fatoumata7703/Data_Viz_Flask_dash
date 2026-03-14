# -*- coding: utf-8 -*-
"""
Web scraping de la page BCEAO pour récupérer les liens vers les PDF
des bilans et comptes de résultat des banques (UMOA).
Page cible: https://www.bceao.int/fr/publications/bilans-et-comptes-de-resultat-des-banques-etablissements-financiers-et-compagnies
"""
import os
import re
import sys
import requests
from urllib.parse import urljoin

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import BCEAO_BASE_URL, BCEAO_PUBLICATIONS_URL, PDF_DOWNLOAD_DIR


def get_page(url, headers=None):
    """Récupère le contenu HTML de la page."""
    if headers is None:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.text


def extract_pdf_links(html, base_url):
    """
    Extrait tous les liens PDF de la page.
    Cherche les balises <a> avec href se terminant par .pdf ou contenant 'pdf'.
    """
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if ".pdf" in href.lower() or "pdf" in href.lower():
            full_url = urljoin(base_url, href)
            text = a.get_text(strip=True) or ""
            # Essayer d'extraire l'année du texte ou de l'URL (ex: "2022", "Bilans ... 2021")
            year_match = re.search(r"20\d{2}", text + " " + href)
            year = int(year_match.group()) if year_match else None
            links.append({"url": full_url, "label": text, "annee": year})
    return links


def download_pdf(url, save_path, headers=None):
    """Télécharge un PDF et le sauvegarde localement."""
    if headers is None:
        headers = {"User-Agent": "Mozilla/5.0"}
    os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)
    resp = requests.get(url, headers=headers, stream=True, timeout=60)
    resp.raise_for_status()
    with open(save_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
    return save_path


def main():
    print("Récupération de la page BCEAO...")
    try:
        html = get_page(BCEAO_PUBLICATIONS_URL)
    except Exception as e:
        print(f"Erreur: {e}")
        return
    def safe(s):
        return (s or "").encode("ascii", "replace").decode() if s else ""

    print("Extraction des liens PDF...")
    links = extract_pdf_links(html, BCEAO_BASE_URL)
    print(f"  {len(links)} lien(s) PDF trouvé(s)")
    for L in links:
        label = safe((L.get("label") or "")[:50])
        url = safe((L.get("url") or "")[:60])
        print(f"  - {L.get('annee')} | {label} | {url}...")
    # Ne garder que les PDF "Bilans et comptes de résultat" (pas les rapports politique monétaire)
    bilans_links = [
        L for L in links
        if "bilans" in (L.get("label") or "").lower() or "bilans" in (L.get("url") or "").lower()
    ]
    if bilans_links:
        print(f"  -> {len(bilans_links)} lien(s) 'Bilans et comptes de résultat'")
    # Téléchargement des PDF bilans
    if bilans_links:
        os.makedirs(PDF_DOWNLOAD_DIR, exist_ok=True)
        print(f"\nTéléchargement dans {PDF_DOWNLOAD_DIR}...")
        for L in bilans_links:
            url = L["url"]
            year = L.get("annee") or "unknown"
            filename = f"bilan_umoa_{year}.pdf"
            path = os.path.join(PDF_DOWNLOAD_DIR, filename)
            try:
                download_pdf(url, path)
                print(f"  OK: {filename}")
            except Exception as e:
                print(f"  Erreur {filename}: {e}")
    elif links:
        print("\nAucun PDF 'Bilans et comptes de résultat' trouvé (liens = autres publications).")
    return links


if __name__ == "__main__":
    main()
