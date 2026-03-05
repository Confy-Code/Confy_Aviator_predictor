(() => {
    console.log('Starting Enhanced Multiplier Tracker...');
    
    const MULTIPLIER_SELECTOR = '.payout';
    const CASHOUT_SELECTOR= '.cashout-value';
    const BETS_COUNT_SELECTOR= '.bets-count';
    const PLAYER_COUNT_SELECTOR= '.player-count';

    const API_ENDPOINT = 'http://localhost:5000/api/multipliers';
    
    // Create visual indicator
    const indicator = document.createElement('div');
    indicator.id = 'aviator-multiplier-tracker';
    indicator.style = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #000;
        color: #0f0;
        padding: 10px 20px;
        font-size: 24px;
        font-weight: bold;
        z-index: 9999;
        border: 2px solid #0f0;
        border-radius: 5px;
        font-family: monospace;
    `;
    document.body.appendChild(indicator);

    let lastMultiplier = null;

    async function captureAndSaveData(currentMultiplier, cashout_element, bets_count_element, player_count_element) {
        try { 
            const payload = {                
                multiplier: currentMultiplier,
                cashout_value: cashout_element,
                bets_count: bets_count_element,
                player_count: player_count_element                               
                                
            };
            
            // Send this to backend
            const response = await fetch(API_ENDPOINT, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                console.error('Failed to save data:', await response.text());
            }
        } catch (error) {
            console.error('Error capturing/saving data:', error);
        }
    }

    function updateMultiplier() {
        const element = document.querySelector(MULTIPLIER_SELECTOR);
        const cashout_element=document.querySelector(CASHOUT_SELECTOR).textContent;
        const bets_count_element=document.querySelector(BETS_COUNT_SELECTOR).textContent;
        const player_count_element=document.querySelector(PLAYER_COUNT_SELECTOR).textContent;
        
        if (element) {
            const text = element.textContent.trim();
            const match = text.match(/(\d+\.\d+)/);
            if (match) {
                const currentMultiplier = parseFloat(match[1]);
                if (currentMultiplier !== lastMultiplier) {
                    lastMultiplier = currentMultiplier;
                    indicator.textContent = `${currentMultiplier.toFixed(2)}x\n${cashout_element}\n${bets_count_element}`;
                    indicator.style.whiteSpace = 'pre'; 
                
                    console.log('Multiplier Updated:', currentMultiplier.toFixed(2));
                    
                    // calls what to send to back-end
                    captureAndSaveData(currentMultiplier, cashout_element, bets_count_element, player_count_element);
                    
                    // Flash effect
                    indicator.style.backgroundColor = '#0f0';
                    indicator.style.color = '#000';
                    setTimeout(() => {
                        indicator.style.backgroundColor = '#000';
                        indicator.style.color = '#0f0';
                    }, 200);
                }
            }
        } else {
            indicator.textContent = 'Element not found';
            indicator.style.backgroundColor = '#f00';
        }
    }

        const observer = new MutationObserver(updateMultiplier);
        observer.observe(document.body, {
            childList: true,
            subtree: true,
            characterData: true,
            attributes: false
        });

        // Fallback polling
        const pollInterval = setInterval(updateMultiplier, 500);
        console.log('Enhanced Tracker active - watching for multiplier changes...');
    })();
    