document.addEventListener('DOMContentLoaded', async () => {
    // Récupération des éléments du DOM
    const token = localStorage.getItem('accessToken');
    const userInfo = document.getElementById('user-info');
    const propertiesList = document.getElementById('properties-list');
    const logoutButton = document.getElementById('logout-button');
    const addPropertyForm = document.getElementById('add-property-form');
    const propertyErrorMessage = document.getElementById('property-error-message');
    const alertsSection = document.getElementById('alerts-section');
    const alertsList = document.getElementById('alerts-list');
    const selectedPropertyLabel = document.getElementById('selected-property-label');
    const consentsSection = document.getElementById('consents-section');
    const consentsList = document.getElementById('consents-list');
    const addConsentForm = document.getElementById('add-consent-form');
    const consentErrorMessage = document.getElementById('consent-error-message');
    let selectedPropertyId = null;

    // 1. Protection de la page
    if (!token) {
        window.location.href = '/login.html';
        return;
    }

    // 2. Logique de Déconnexion
    logoutButton.addEventListener('click', () => {
        localStorage.removeItem('accessToken');
        window.location.href = '/login.html';
    });

    // 3. Préparation des requêtes API
    const headers = {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    };

    // 4. Fonctions pour interagir avec l'API

    async function fetchAndDisplayConsents(propertyId) {
        try {
            consentsSection.classList.remove('hidden');
            consentsList.innerHTML = '<li>Chargement des consentements...</li>';
            const response = await fetch(`/api/properties/${propertyId}/consents/`, { headers });
            if (!response.ok) throw new Error('Failed to fetch consents');

            const consents = await response.json();
            consentsList.innerHTML = '';

            if (consents.length === 0) {
                consentsList.innerHTML = '<li>Aucun consentement pour ce bien.</li>';
            } else {
                consents.forEach(consent => {
                    const li = document.createElement('li');
                    li.textContent = `${consent.holder_email} - Statut: ${consent.status}`;
                    consentsList.appendChild(li);
                });
            }
        } catch (error) {
            console.error('Error fetching consents:', error);
            consentsList.innerHTML = '<li>Erreur lors du chargement des consentements.</li>';
        }
    }

    async function fetchAndDisplayAlerts(propertyId, propertyLabel) {
        selectedPropertyId = propertyId;
        try {
            selectedPropertyLabel.textContent = `"${propertyLabel}"`;
            alertsSection.classList.remove('hidden');
            alertsList.innerHTML = '<li>Chargement des alertes...</li>';
            const response = await fetch(`/api/properties/${propertyId}/alerts/`, { headers });
            if (!response.ok) throw new Error('Failed to fetch alerts');

            const alerts = await response.json();
            alertsList.innerHTML = '';

            if (alerts.length === 0) {
                alertsList.innerHTML = '<li>Aucune alerte pour ce bien.</li>';
            } else {
                alerts.forEach(alert => {
                    const li = document.createElement('li');
                    const alertDate = new Date(alert.created_at).toLocaleString('fr-FR');
                    li.textContent = `[${alertDate}] - Type: ${alert.event_type}`;
                    alertsList.appendChild(li);
                });
            }
            await fetchAndDisplayConsents(propertyId);
        } catch (error) {
            console.error('Error fetching alerts:', error);
            alertsList.innerHTML = '<li>Erreur lors du chargement des alertes.</li>';
        }
    }

    async function fetchAndDisplayProperties() {
        try {
            const response = await fetch('/api/properties/', { headers });
            if (!response.ok) throw new Error('Failed to fetch properties');
            const properties = await response.json();
            propertiesList.innerHTML = '';
            properties.forEach(property => {
                const li = document.createElement('li');
                const propertyDiv = document.createElement('div');
                propertyDiv.className = 'property-item';
                const contentContainer = document.createElement('div');
                contentContainer.className = 'property-content';

                const showTextView = () => {
                    contentContainer.innerHTML = `
                        <span class="clickable" title="Cliquer pour voir les alertes">${property.label} (${property.status})
                        <div class="buttons">
                            <button class="edit-btn">Modifier</button>
                            <button class="delete-btn">Supprimer</button>
                        </div>
                        </span>`;
                    contentContainer.querySelector('.clickable').onclick = () => fetchAndDisplayAlerts(property.id, property.label);
                    contentContainer.querySelector('.edit-btn').onclick = () => showEditView();
                    contentContainer.querySelector('.delete-btn').onclick = async () => {
                        if (confirm('Êtes-vous sûr de vouloir supprimer le bien "${property.label}" ?')) {
                            try {
                                const deleteResponse = await fetch(`/api/properties/${property.id}`, {
                                    method: 'DELETE',
                                    headers: headers
                                });
                                if (deleteResponse.ok) {
                                    await fetchAndDisplayProperties();
                                    alertsSection.classList.add('hidden');
                                    consentsSection.classList.add('hidden');
                                } else { alert('Erreur lors de la suppression du bien.'); }
                            } catch (error) { console.error('Delete error:', error); alert('Erreur réseau.'); }
                        }
                    };
                };

                const showEditView = () => {
                    contentContainer.innerHTML = `
                        <form class="edit-form">
                            <input type="text" name="label" value="${property.label}" required>
                            <input type="text" name="pdl" value="${property.pdl}" required>
                            <input type="text" name="address" value="${property.address}" required>
                            <button type="submit">Enregistrer</button>
                            <button type="button" class="cancel-btn">Annuler</button>
                        </form>`;
                    const editForm = contentContainer.querySelector('.edit-form');
                    editForm.querySelector('.cancel-btn').onclick = () => showTextView();
                    editForm.addEventListener('submit', async (e) => {
                        e.preventDefault();
                        const formData = new FormData(editForm);
                        const updatedData = Object.fromEntries(formData.entries());
                        try {
                            const response = await fetch(`/api/properties/${property.id}`, {
                                method: 'PUT',
                                headers: headers,
                                body: JSON.stringify(updatedData)
                            });
                            if (response.ok) {
                                await fetchAndDisplayProperties();
                                alertsSection.classList.add('hidden');
                                consentsSection.classList.add('hidden');
                            } else { alert('Erreur lors de la mise à jour.'); }
                        } catch (error) { console.error('Update error:', error); alert('Erreur réseau.'); }
                    });
                };

                showTextView();
                propertyDiv.appendChild(contentContainer);
                li.appendChild(propertyDiv);
                propertiesList.appendChild(li);
            });
        } catch (error) {
            console.error('Error fetching properties:', error);
            propertiesList.innerHTML = '<li>Erreur lors du chargement des propriétés.</li>';
        }
    }

    addPropertyForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        propertyErrorMessage.textContent = '';
        const formData = new FormData(addPropertyForm);
        const propertyData = {
            label: formData.get('label'),
            pdl: formData.get('pdl'),
            address: formData.get('address'),
            status: 'EMPTY'
        };
        try {
            const response = await fetch('/api/properties/', {
                method: 'POST',
                headers: headers,
                body: JSON.stringify(propertyData)
            });
            if (response.ok) {
                addPropertyForm.reset();
                await fetchAndDisplayProperties();
                alert('Bien ajouté avec succès !');
            } else {
                const error = await response.json();
                propertyErrorMessage.textContent = error.detail || 'Erreur lors de l\'ajout.';
            }
        } catch (error) {
            propertyErrorMessage.textContent = 'Erreur réseau.';
            console.error('Add property error:', error);
        }
    });

    addConsentForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        consentErrorMessage.textContent = '';
        if (!selectedPropertyId) {
            consentErrorMessage.textContent = 'Veuillez d\'abord sélectionner un bien.';
            return;
        }
        const formData = new FormData(addConsentForm);
        const consentData = {
            property_id: selectedPropertyId,
            holder_name: formData.get('holder_name'),
            holder_email: formData.get('holder_email')
        };
        try {
            const response = await fetch('/api/consents/', {
                method: 'POST',
                headers: headers,
                body: JSON.stringify(consentData)
            });
            if (response.ok) {
                addConsentForm.reset();
                await fetchAndDisplayConsents(selectedPropertyId);
                alert('Invitation envoyée avec succès !');
            } else {
                const error = await response.json();
                consentErrorMessage.textContent = error.detail || 'Erreur lors de l\'envoi.';
            }
        } catch (error) {
            consentErrorMessage.textContent = 'Erreur réseau.';
            console.error('Add consent error:', error);
        }
    });

    // 6. Initialisation de la page
    async function initializeDashboard() {
        try {
            const userResponse = await fetch('/api/users/me/', { headers });
            if (!userResponse.ok) throw new Error('Failed to fetch user');
            const user = await userResponse.json();
            userInfo.textContent = `Connecté en tant que : ${user.email}`;
            await fetchAndDisplayProperties();
        } catch (error) {
            console.error('Initialization error:', error);
            localStorage.removeItem('accessToken');
            window.location.href = '/login.html';
        }
    }

    initializeDashboard();
});