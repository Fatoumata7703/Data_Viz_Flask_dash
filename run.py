from app import server

if __name__ == '__main__':
    print("=" * 60)
    print("Démarrage de l'application Flash Dash")
    print("=" * 60)
    print("\nDashboards disponibles:")
    print("   • Page d'accueil: http://localhost:5000/")
    print("   • Dashboard Photovoltaïque: http://localhost:5000/dash1")
    print("   • Dashboard Assurance: http://localhost:5000/dash2")
    print("   • Dashboard Bancaire: http://localhost:5000/bank")
    print("   • Dashboard Hospitalier: http://localhost:5000/pro")
    print("\n" + "=" * 60)
    print("Appuyez sur Ctrl+C pour arrêter le serveur")
    print("=" * 60 + "\n")
    
    server.run(debug=True, host='0.0.0.0', port=5000)
