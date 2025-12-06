#!/usr/bin/env python3
"""
Altseason Sentinel - Market Intelligence Dashboard
Monitors critical crypto market conditions for altseason opportunities

Built by Mike B. for QuantumShieldLabs LLC
"""

import requests
import time
import json
import smtplib
import csv
import os
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
import yaml

console = Console()


class AltseasonSentinel:
    def __init__(self, config_path='config.yaml'):
        """Initialize the sentinel with configuration"""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.data_log = []
        self.alert_history = []
        self.last_prices = {}
        
        # Alert thresholds - BTC critical levels
        self.btc_levels = {
            'critical_low': 104000,
            'critical_high': 105000,
            'bull_confirmation': 116000,
            'breakdown': 88000
        }
        
        self.ltc_cycle_top = 130  # Litecoin cycle top indicator
        
        # Target date (mid-December altseason window)
        self.target_date = datetime(2025, 12, 15)
        
    def fetch_coingecko_data(self):
        """Fetch price and market data from CoinGecko"""
        try:
            url = "https://api.coingecko.com/api/v3/coins/markets"
            params = {
                'vs_currency': 'usd',
                'ids': 'bitcoin,ethereum,litecoin',
                'order': 'market_cap_desc',
                'sparkline': 'false',
                'price_change_percentage': '24h'
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            result = {}
            for coin in data:
                result[coin['id']] = {
                    'price': coin['current_price'],
                    'market_cap': coin['market_cap'],
                    'volume_24h': coin['total_volume'],
                    'change_24h': coin['price_change_percentage_24h']
                }
            
            return result
        except Exception as e:
            console.print(f"[red]Error fetching CoinGecko data: {e}[/red]")
            return None
    
    def fetch_dominance_data(self):
        """Fetch dominance metrics from CoinGecko"""
        try:
            url = "https://api.coingecko.com/api/v3/global"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()['data']
            
            btc_dominance = data['market_cap_percentage'].get('btc', 0)
            eth_dominance = data['market_cap_percentage'].get('eth', 0)
            
            # Calculate "Others" dominance (everything except BTC and ETH)
            others_dominance = 100 - btc_dominance - eth_dominance
            
            # Estimate stablecoin dominance (approximate)
            stablecoin_dominance = 5.0  # Placeholder - would need separate API
            
            return {
                'btc_dominance': btc_dominance,
                'eth_dominance': eth_dominance,
                'others_dominance': others_dominance,
                'stablecoin_dominance': stablecoin_dominance,
                'total_market_cap': data['total_market_cap']['usd']
            }
        except Exception as e:
            console.print(f"[red]Error fetching dominance data: {e}[/red]")
            return None
    
    def fetch_old_coins_data(self):
        """Fetch data for 'old coin revival' candidates"""
        old_coins = [
            'internet-computer', 'neo', 'ethereum-classic', 
            'filecoin', 'stellar', 'dash', 'zcash'
        ]
        
        try:
            ids = ','.join(old_coins)
            url = "https://api.coingecko.com/api/v3/coins/markets"
            params = {
                'vs_currency': 'usd',
                'ids': ids,
                'order': 'market_cap_desc',
                'sparkline': 'false',
                'price_change_percentage': '24h,7d'
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            result = {}
            for coin in data:
                # Calculate volume to market cap ratio (activity indicator)
                vol_mcap_ratio = (coin['total_volume'] / coin['market_cap'] * 100) if coin['market_cap'] > 0 else 0
                
                result[coin['id']] = {
                    'symbol': coin['symbol'].upper(),
                    'price': coin['current_price'],
                    'market_cap': coin['market_cap'],
                    'volume_24h': coin['total_volume'],
                    'change_24h': coin.get('price_change_percentage_24h', 0) or 0,
                    'change_7d': coin.get('price_change_percentage_7d_in_currency', 0) or 0,
                    'vol_mcap_ratio': vol_mcap_ratio
                }
            
            return result
        except Exception as e:
            console.print(f"[red]Error fetching old coins data: {e}[/red]")
            return None

    def calculate_altseason_score(self, dominance, btc_price):
        """
        Calculate altseason probability score (0-100%)
        Based on multiple market structure signals
        """
        score = 0
        signals = []
        
        if not dominance or not btc_price:
            return 50, ["Insufficient data"]
        
        # Signal 1: BTC Dominance < 61% (altseason threshold)
        if dominance['btc_dominance'] < 61:
            score += 25
            signals.append("✅ BTC dominance < 61%")
        elif dominance['btc_dominance'] < 64:
            score += 15
            signals.append("⏳ BTC dominance approaching threshold")
        else:
            signals.append("❌ BTC dominance too high")
        
        # Signal 2: Others Dominance > 30%
        if dominance['others_dominance'] > 30:
            score += 25
            signals.append("✅ Others dominance > 30%")
        elif dominance['others_dominance'] > 25:
            score += 15
            signals.append("⏳ Others dominance building")
        else:
            signals.append("❌ Others dominance weak")
        
        # Signal 3: Stablecoin dominance rejection (capital rotating out)
        if dominance['stablecoin_dominance'] < 6:
            score += 15
            signals.append("✅ Stablecoin dom rejected")
        else:
            score += 5
            signals.append("📊 Stablecoin dom neutral")
        
        # Signal 4: BTC holding key support levels
        if btc_price >= self.btc_levels['critical_low']:
            score += 20
            signals.append("✅ BTC holding key support")
        elif btc_price >= self.btc_levels['breakdown']:
            score += 10
            signals.append("⚠️ BTC in caution zone")
        else:
            signals.append("🚨 BTC below key support")
        
        # Signal 5: Time remaining in altseason window
        days_remaining = (self.target_date - datetime.now()).days
        if 0 < days_remaining <= 45:
            score += 15
            signals.append(f"⏳ {days_remaining} days remaining")
        elif days_remaining > 45:
            score += 5
            signals.append(f"📅 {days_remaining} days to target")
        else:
            signals.append("⏰ Past target date")
        
        return min(score, 100), signals

    def check_alerts(self, data):
        """Check for alert conditions and return list of alerts"""
        alerts = []
        
        if not data.get('prices'):
            return alerts
        
        btc_price = data['prices'].get('bitcoin', {}).get('price', 0)
        ltc_price = data['prices'].get('litecoin', {}).get('price', 0)
        dominance = data.get('dominance', {})
        
        # Critical: BTC below $104K
        if btc_price and btc_price < self.btc_levels['critical_low']:
            alerts.append({
                'level': 'CRITICAL',
                'message': f"🚨 BTC BELOW ${self.btc_levels['critical_low']:,} - Currently ${btc_price:,.0f}\nACTION: Reduce alt exposure NOW"
            })
        
        # Critical: BTC breakdown below $88K
        if btc_price and btc_price < self.btc_levels['breakdown']:
            alerts.append({
                'level': 'CRITICAL',
                'message': f"🚨 BTC BREAKDOWN - Currently ${btc_price:,.0f}\nACTION: Emergency risk reduction"
            })
        
        # Bullish: BTC above $116K confirmation
        if btc_price and btc_price >= self.btc_levels['bull_confirmation']:
            alerts.append({
                'level': 'BULLISH',
                'message': f"🎯 BTC BULL CONFIRMATION - ${btc_price:,.0f}\nACTION: Optimal conditions for alts"
            })
        
        # Warning: Litecoin cycle top signal
        if ltc_price and ltc_price >= self.ltc_cycle_top:
            alerts.append({
                'level': 'WARNING',
                'message': f"🔔 LITECOIN CYCLE TOP SIGNAL - ${ltc_price:.2f}\nACTION: Consider aggressive profit taking"
            })
        
        # Bullish: BTC dominance falling below 60%
        if dominance.get('btc_dominance', 100) < 60:
            alerts.append({
                'level': 'BULLISH',
                'message': f"🎯 BTC DOMINANCE < 60% - ALTSEASON CONFIRMED at {dominance['btc_dominance']:.1f}%\nACTION: Optimal conditions for alt rotation"
            })
        
        # Opportunity: Old coin volume spikes
        old_coins = data.get('old_coins', {})
        for coin_id, coin_data in old_coins.items():
            if coin_data['vol_mcap_ratio'] > 20 and coin_data['change_24h'] > 15:
                alerts.append({
                    'level': 'OPPORTUNITY',
                    'message': f"💎 {coin_data['symbol']} - Volume spike! +{coin_data['change_24h']:.0f}% with {coin_data['vol_mcap_ratio']:.0f}% vol/mcap\nACTION: Check similar era bags in your wallets"
                })
        
        return alerts

    def send_discord_notification(self, message, level="INFO"):
        """Send notification to Discord webhook"""
        if not self.config.get('discord', {}).get('enabled', False):
            return
        
        webhook_url = self.config['discord'].get('webhook_url', '')
        if not webhook_url or webhook_url == 'YOUR_DISCORD_WEBHOOK_URL':
            return
        
        # Color coding by level
        colors = {
            'CRITICAL': 16711680,  # Red
            'WARNING': 16776960,   # Yellow
            'BULLISH': 65280,      # Green
            'OPPORTUNITY': 65535,  # Cyan
            'INFO': 3447003        # Blue
        }
        
        embed = {
            "title": f"🚀 ALTSEASON SENTINEL - {level}",
            "description": message,
            "color": colors.get(level, 3447003),
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {"text": "Altseason Sentinel | QuantumShieldLabs"}
        }
        
        try:
            requests.post(webhook_url, json={"embeds": [embed]}, timeout=10)
        except Exception as e:
            console.print(f"[red]Discord notification failed: {e}[/red]")

    def send_email_notification(self, subject, message):
        """Send email notification for critical alerts"""
        if not self.config.get('email', {}).get('enabled', False):
            return
        
        email_config = self.config['email']
        
        try:
            msg = MIMEMultipart()
            msg['From'] = email_config['from_email']
            msg['To'] = email_config['to_email']
            msg['Subject'] = f"[ALTSEASON SENTINEL] {subject}"
            
            body = f"""
            ALTSEASON SENTINEL ALERT
            ========================
            
            {message}
            
            Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            
            --
            Altseason Sentinel | QuantumShieldLabs
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
            server.starttls()
            server.login(email_config['from_email'], email_config['password'])
            server.send_message(msg)
            server.quit()
            
        except Exception as e:
            console.print(f"[red]Email notification failed: {e}[/red]")

    def log_data(self, data):
        """Log data to CSV file"""
        if not self.config.get('logging', {}).get('enabled', False):
            return
        
        log_file = self.config['logging'].get('file', 'altseason_data.csv')
        file_exists = os.path.exists(log_file)
        
        try:
            with open(log_file, 'a', newline='') as f:
                writer = csv.writer(f)
                
                if not file_exists:
                    writer.writerow([
                        'timestamp', 'btc_price', 'btc_change_24h',
                        'btc_dominance', 'eth_dominance', 'others_dominance',
                        'altseason_score', 'ltc_price'
                    ])
                
                prices = data.get('prices', {})
                dominance = data.get('dominance', {})
                
                writer.writerow([
                    datetime.now().isoformat(),
                    prices.get('bitcoin', {}).get('price', 0),
                    prices.get('bitcoin', {}).get('change_24h', 0),
                    dominance.get('btc_dominance', 0),
                    dominance.get('eth_dominance', 0),
                    dominance.get('others_dominance', 0),
                    data.get('altseason_score', 0),
                    prices.get('litecoin', {}).get('price', 0)
                ])
        except Exception as e:
            console.print(f"[red]Data logging failed: {e}[/red]")

    def build_dashboard(self, data):
        """Build the terminal dashboard display"""
        layout = Layout()
        
        # Calculate days remaining
        days_remaining = (self.target_date - datetime.now()).days
        
        # Header
        header_text = Text()
        header_text.append("🚀 ALTSEASON SENTINEL 🚀\n", style="bold magenta")
        header_text.append(f"Target Date: {self.target_date.strftime('%b %d, %Y')} ", style="cyan")
        header_text.append(f"({days_remaining} days remaining)\n", style="yellow")
        header_text.append(f"Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", style="dim")
        
        # Altseason Score
        score = data.get('altseason_score', 0)
        signals = data.get('signals', [])
        
        if score >= 70:
            score_color = "bold green"
            score_emoji = "🟢"
        elif score >= 50:
            score_color = "bold yellow"
            score_emoji = "🟡"
        else:
            score_color = "bold red"
            score_emoji = "🔴"
        
        score_text = Text()
        score_text.append(f"\n🎯 ALTSEASON PROBABILITY: ", style="bold white")
        score_text.append(f"{score}%", style=score_color)
        score_text.append(f" {score_emoji}\n\n", style="bold")
        
        for signal in signals:
            score_text.append(f"{signal}\n", style="white")
        
        # Bitcoin Critical Levels Table
        prices = data.get('prices', {})
        btc_data = prices.get('bitcoin', {})
        btc_price = btc_data.get('price', 0)
        btc_change = btc_data.get('change_24h', 0)
        
        btc_table = Table(title="Bitcoin Critical Levels", show_header=True, header_style="bold cyan")
        btc_table.add_column("Level", style="white")
        btc_table.add_column("Price", style="cyan")
        btc_table.add_column("Status", style="white")
        
        # Add BTC level rows
        btc_table.add_row(
            "Critical Low", 
            f"${self.btc_levels['critical_low']:,}",
            "✅ Above" if btc_price >= self.btc_levels['critical_low'] else "🚨 BELOW"
        )
        btc_table.add_row(
            "Critical High", 
            f"${self.btc_levels['critical_high']:,}",
            "✅ Above" if btc_price >= self.btc_levels['critical_high'] else "⚠️ Below"
        )
        btc_table.add_row(
            "Bull Confirmation", 
            f"${self.btc_levels['bull_confirmation']:,}",
            "🎯 CONFIRMED" if btc_price >= self.btc_levels['bull_confirmation'] else "❌ Below"
        )
        btc_table.add_row(
            "Breakdown", 
            f"${self.btc_levels['breakdown']:,}",
            "✅ Above" if btc_price >= self.btc_levels['breakdown'] else "🚨 BREAKDOWN"
        )
        
        change_style = "green" if btc_change >= 0 else "red"
        btc_table.add_row(
            "Current Price", 
            f"${btc_price:,.0f}",
            f"[{change_style}]{btc_change:+.2f}%[/{change_style}]"
        )
        
        # Dominance Table
        dominance = data.get('dominance', {})
        
        dom_table = Table(title="Dominance Metrics", show_header=True, header_style="bold cyan")
        dom_table.add_column("Metric", style="white")
        dom_table.add_column("Value", style="cyan")
        dom_table.add_column("Signal", style="white")
        
        btc_dom = dominance.get('btc_dominance', 0)
        others_dom = dominance.get('others_dominance', 0)
        
        dom_table.add_row(
            "BTC Dominance",
            f"{btc_dom:.2f}%",
            "🟢 Falling" if btc_dom < 61 else "🔴 High"
        )
        dom_table.add_row(
            "Others Dominance",
            f"{others_dom:.2f}%",
            "🟢 Rising" if others_dom > 30 else "⏳ Building"
        )
        dom_table.add_row(
            "Stablecoin Dom (est)",
            f"{dominance.get('stablecoin_dominance', 0):.2f}%",
            "📊"
        )
        
        # Old Coins Table
        old_coins = data.get('old_coins', {})
        
        old_table = Table(title="Old Coin Revival Watch", show_header=True, header_style="bold cyan")
        old_table.add_column("Coin", style="white")
        old_table.add_column("Price", style="cyan")
        old_table.add_column("24h", style="white")
        old_table.add_column("Vol/MCap", style="white")
        
        # Sort by 24h change
        sorted_coins = sorted(old_coins.items(), key=lambda x: x[1].get('change_24h', 0), reverse=True)
        
        for coin_id, coin_data in sorted_coins[:5]:
            change = coin_data.get('change_24h', 0)
            change_style = "green" if change >= 0 else "red"
            vol_ratio = coin_data.get('vol_mcap_ratio', 0)
            
            hot = "🔥 " if change > 20 and vol_ratio > 15 else ""
            
            old_table.add_row(
                f"{hot}{coin_data['symbol']}",
                f"${coin_data['price']:,.2f}",
                f"[{change_style}]{change:+.1f}%[/{change_style}]",
                f"{vol_ratio:.1f}%"
            )
        
        # LTC Cycle Top Check
        ltc_price = prices.get('litecoin', {}).get('price', 0)
        ltc_text = Text()
        if ltc_price >= self.ltc_cycle_top:
            ltc_text.append(f"\n🔔 LITECOIN CYCLE TOP WARNING: ${ltc_price:.2f} (above ${self.ltc_cycle_top}!)\n", style="bold yellow")
        else:
            ltc_text.append(f"\n📊 Litecoin: ${ltc_price:.2f} (watch ${self.ltc_cycle_top})\n", style="dim")
        
        # Combine everything
        console.clear()
        console.print(Panel(header_text, border_style="magenta"))
        console.print(Panel(score_text, title="Market Signals", border_style="cyan"))
        console.print(btc_table)
        console.print(dom_table)
        console.print(old_table)
        console.print(ltc_text)

    def fetch_all_data(self):
        """Fetch all market data"""
        data = {}
        
        # Fetch prices
        prices = self.fetch_coingecko_data()
        time.sleep(1)  # Rate limiting
        
        # Fetch dominance
        dominance = self.fetch_dominance_data()
        time.sleep(1)  # Rate limiting
        
        # Fetch old coins
        old_coins = self.fetch_old_coins_data()
        
        if prices:
            data['prices'] = prices
        if dominance:
            data['dominance'] = dominance
        if old_coins:
            data['old_coins'] = old_coins
        
        # Calculate altseason score
        btc_price = prices.get('bitcoin', {}).get('price') if prices else None
        score, signals = self.calculate_altseason_score(dominance, btc_price)
        data['altseason_score'] = score
        data['signals'] = signals
        
        return data

    def process_alerts(self, data):
        """Process and send alerts"""
        alerts = self.check_alerts(data)
        
        for alert in alerts:
            # Avoid duplicate alerts (check if sent in last 30 minutes)
            alert_key = f"{alert['level']}:{alert['message'][:50]}"
            threshold = self.config.get('alerts', {}).get('duplicate_threshold_minutes', 30)
            recent_alerts = [a for a in self.alert_history if 
                           datetime.now() - a['timestamp'] < timedelta(minutes=threshold)]
            
            if any(a['key'] == alert_key for a in recent_alerts):
                continue  # Skip duplicate
            
            # Send notifications
            console.print(f"\n[bold]{alert['level']}[/bold]: {alert['message']}")
            
            discord_levels = self.config.get('alerts', {}).get('discord_levels', ['CRITICAL', 'BULLISH', 'WARNING', 'OPPORTUNITY'])
            if alert['level'] in discord_levels:
                self.send_discord_notification(alert['message'], alert['level'])
            
            email_levels = self.config.get('alerts', {}).get('email_levels', ['CRITICAL'])
            if alert['level'] in email_levels:
                self.send_email_notification(alert['level'], alert['message'])
            
            # Log alert
            self.alert_history.append({
                'timestamp': datetime.now(),
                'key': alert_key,
                'alert': alert
            })

    def run(self):
        """Main monitoring loop"""
        console.print("[bold green]🚀 Altseason Sentinel Started![/bold green]")
        console.print(f"Update interval: {self.config['update_interval_seconds']} seconds\n")
        
        # Send startup notification
        self.send_discord_notification(
            "Altseason Sentinel is now monitoring markets!\n\n"
            "Tracking:\n"
            "• BTC critical levels\n"
            "• Dominance metrics\n"
            "• Old coin revivals\n"
            "• Altseason probability",
            "INFO"
        )
        
        while True:
            try:
                # Fetch data
                data = self.fetch_all_data()
                
                # Build and display dashboard
                self.build_dashboard(data)
                
                # Process alerts
                self.process_alerts(data)
                
                # Log data
                self.log_data(data)
                
                # Wait for next update
                time.sleep(self.config['update_interval_seconds'])
                
            except KeyboardInterrupt:
                console.print("\n[yellow]👋 Sentinel stopped. See you next time![/yellow]")
                self.send_discord_notification("Altseason Sentinel has stopped monitoring.", "INFO")
                break
            except Exception as e:
                console.print(f"[red]Error in main loop: {e}[/red]")
                time.sleep(60)  # Wait a minute before retrying


if __name__ == "__main__":
    sentinel = AltseasonSentinel()
    sentinel.run()
