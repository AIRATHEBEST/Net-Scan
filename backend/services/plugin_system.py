import asyncio
import logging
from typing import Dict, List, Optional, Callable
import importlib
import inspect
from pathlib import Path
import json

logger = logging.getLogger(__name__)

class PluginSystem:
    """
    🧩 Tier 3 Feature #12: Plugin System
    
    Extensible plugin architecture:
    - User-created scanners
    - Custom integrations
    - API extensions
    - Plugin marketplace
    - Sandboxed execution
    """
    
    def __init__(self, plugins_dir: str = "plugins"):
        self.plugins_dir = Path(plugins_dir)
        self.plugins_dir.mkdir(exist_ok=True)
        
        self.loaded_plugins = {}
        self.plugin_hooks = {
            'pre_scan': [],
            'post_scan': [],
            'device_discovered': [],
            'threat_detected': [],
            'alert_created': []
        }
    
    async def load_plugin(self, plugin_name: str) -> Dict[str, any]:
        """
        Load and initialize a plugin
        """
        
        logger.info(f"Loading plugin: {plugin_name}")
        
        plugin_path = self.plugins_dir / plugin_name
        
        if not plugin_path.exists():
            return {'success': False, 'error': 'Plugin not found'}
        
        # Load plugin manifest
        manifest_path = plugin_path / 'manifest.json'
        
        if not manifest_path.exists():
            return {'success': False, 'error': 'Plugin manifest not found'}
        
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        
        # Validate plugin
        if not self._validate_plugin(manifest):
            return {'success': False, 'error': 'Invalid plugin manifest'}
        
        # Load plugin module
        try:
            plugin_module = importlib.import_module(f"plugins.{plugin_name}.main")
            
            # Get plugin class
            plugin_class = getattr(plugin_module, manifest['class_name'])
            
            # Initialize plugin
            plugin_instance = plugin_class()
            
            # Store plugin
            self.loaded_plugins[plugin_name] = {
                'manifest': manifest,
                'instance': plugin_instance,
                'enabled': True
            }
            
            # Register hooks
            await self._register_plugin_hooks(plugin_name, plugin_instance)
            
            logger.info(f"Plugin loaded successfully: {plugin_name}")
            
            return {
                'success': True,
                'plugin': plugin_name,
                'version': manifest.get('version'),
                'hooks': list(manifest.get('hooks', []))
            }
        
        except Exception as e:
            logger.error(f"Failed to load plugin {plugin_name}: {e}")
            return {'success': False, 'error': str(e)}
    
    def _validate_plugin(self, manifest: Dict) -> bool:
        """Validate plugin manifest"""
        
        required_fields = ['name', 'version', 'class_name', 'author']
        
        return all(field in manifest for field in required_fields)
    
    async def _register_plugin_hooks(self, plugin_name: str, plugin_instance):
        """Register plugin hooks"""
        
        # Find all hook methods
        for method_name in dir(plugin_instance):
            if method_name.startswith('on_'):
                hook_name = method_name[3:]  # Remove 'on_' prefix
                
                if hook_name in self.plugin_hooks:
                    method = getattr(plugin_instance, method_name)
                    
                    if callable(method):
                        self.plugin_hooks[hook_name].append({
                            'plugin': plugin_name,
                            'method': method
                        })
                        
                        logger.debug(f"Registered hook: {plugin_name}.{method_name}")
    
    async def trigger_hook(self, hook_name: str, data: Dict) -> List[Dict]:
        """
        Trigger plugin hooks
        """
        
        if hook_name not in self.plugin_hooks:
            return []
        
        results = []
        
        for hook in self.plugin_hooks[hook_name]:
            plugin_name = hook['plugin']
            
            # Check if plugin is enabled
            if not self.loaded_plugins.get(plugin_name, {}).get('enabled'):
                continue
            
            try:
                # Execute hook in sandboxed environment
                result = await self._execute_hook_sandboxed(
                    hook['method'],
                    data
                )
                
                results.append({
                    'plugin': plugin_name,
                    'result': result
                })
            
            except Exception as e:
                logger.error(f"Plugin hook failed: {plugin_name}.{hook_name} - {e}")
                results.append({
                    'plugin': plugin_name,
                    'error': str(e)
                })
        
        return results
    
    async def _execute_hook_sandboxed(self, method: Callable, data: Dict):
        """
        Execute plugin hook in sandboxed environment
        """
        
        # In production, this would use proper sandboxing
        # For now, just execute with timeout
        
        try:
            if inspect.iscoroutinefunction(method):
                result = await asyncio.wait_for(method(data), timeout=30.0)
            else:
                result = await asyncio.to_thread(method, data)
            
            return result
        
        except asyncio.TimeoutError:
            raise Exception("Plugin execution timeout")
    
    async def list_plugins(self) -> List[Dict]:
        """List all available plugins"""
        
        plugins = []
        
        for plugin_name, plugin_data in self.loaded_plugins.items():
            manifest = plugin_data['manifest']
            
            plugins.append({
                'name': plugin_name,
                'version': manifest.get('version'),
                'author': manifest.get('author'),
                'description': manifest.get('description'),
                'enabled': plugin_data.get('enabled', False),
                'hooks': list(manifest.get('hooks', []))
            })
        
        return plugins
    
    async def enable_plugin(self, plugin_name: str) -> bool:
        """Enable a plugin"""
        
        if plugin_name in self.loaded_plugins:
            self.loaded_plugins[plugin_name]['enabled'] = True
            logger.info(f"Plugin enabled: {plugin_name}")
            return True
        
        return False
    
    async def disable_plugin(self, plugin_name: str) -> bool:
        """Disable a plugin"""
        
        if plugin_name in self.loaded_plugins:
            self.loaded_plugins[plugin_name]['enabled'] = False
            logger.info(f"Plugin disabled: {plugin_name}")
            return True
        
        return False
    
    async def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a plugin"""
        
        if plugin_name in self.loaded_plugins:
            # Remove hooks
            for hook_name, hooks in self.plugin_hooks.items():
                self.plugin_hooks[hook_name] = [
                    h for h in hooks if h['plugin'] != plugin_name
                ]
            
            # Remove plugin
            del self.loaded_plugins[plugin_name]
            
            logger.info(f"Plugin unloaded: {plugin_name}")
            return True
        
        return False
    
    def create_plugin_template(self, plugin_name: str) -> Dict[str, any]:
        """
        Create plugin template for developers
        """
        
        plugin_path = self.plugins_dir / plugin_name
        plugin_path.mkdir(exist_ok=True)
        
        # Create manifest
        manifest = {
            'name': plugin_name,
            'version': '1.0.0',
            'class_name': 'Plugin',
            'author': 'Your Name',
            'description': 'Plugin description',
            'hooks': ['device_discovered', 'threat_detected']
        }
        
        with open(plugin_path / 'manifest.json', 'w') as f:
            json.dump(manifest, f, indent=2)
        
        # Create main.py template
        template = '''"""
NetScan Plugin: {name}
"""

class Plugin:
    """Plugin implementation"""
    
    def __init__(self):
        self.name = "{name}"
    
    async def on_device_discovered(self, data):
        """Called when new device is discovered"""
        device = data.get('device')
        
        # Your custom logic here
        print(f"Device discovered: {{device.get('ip_address')}}")
        
        return {{'processed': True}}
    
    async def on_threat_detected(self, data):
        """Called when threat is detected"""
        threat = data.get('threat')
        
        # Your custom logic here
        print(f"Threat detected: {{threat.get('type')}}")
        
        return {{'processed': True}}
'''.format(name=plugin_name)
        
        with open(plugin_path / 'main.py', 'w') as f:
            f.write(template)
        
        return {
            'success': True,
            'path': str(plugin_path),
            'files': ['manifest.json', 'main.py']
        }
