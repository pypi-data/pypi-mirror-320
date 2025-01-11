import base64
import zlib

TRIGGERS_IDS = [22, 23, 24, 25, 26, 27, 28, 31, 32, 33, 55, 56, 57, 58, 59, 899, 901, 1006, 1007, 1049, 1268, 1346, 1347, 1520, 1585, 1595, 1611, 1612, 1613, 1615, 1616, 1811, 1812, 1814, 1815, 1816, 1817, 1818, 1819, 1912, 1913, 1914, 1915, 1916, 1917, 1932, 1934, 1935, 2015, 2016, 2062, 2066, 2067, 2068, 2899, 2900, 2901, 2903, 2904, 2905, 2907, 2909, 2910, 2911, 2912, 2913, 2914, 2915, 2916, 2917, 2919, 2920, 2921, 2922, 2923, 2924, 2925, 2999, 3006, 3007, 3008, 3009, 3010, 3011, 3012, 3013, 3014, 3015, 3016, 3017, 3018, 3019, 3020, 3021, 3022, 3023, 3024, 3029, 3030, 3031, 3032, 3033, 3600, 3602, 3603, 3604, 3605, 3606, 3607, 3608, 3609, 3612, 3613, 3614, 3615, 3617, 3618, 3619, 3620, 3640, 3641, 3642, 3643, 3660, 3661, 3662]

class GDLevelDecryptor:
    def __init__(self, encrypted_level_string) -> None:
        self.encrypted_string = encrypted_level_string

    def decrypt(self):
        return self.decode_level(self.load_level(self.encrypted_string), False)

    def load_level(self, level_content):
        parsed_level = self.parse_string_to_dict(level_content)
        objects_data = parsed_level["4"]
        return objects_data

    def decode_level(self, level_data: str, is_official_level: bool) -> str:
        if is_official_level:
            level_data = "H4sIAAAAAAAAA" + level_data
        base64_decoded = base64.urlsafe_b64decode(level_data.encode())
        # window_bits = 15 | 32 will autodetect gzip or not
        decompressed = zlib.decompress(base64_decoded, 15 | 32)
        return decompressed.decode()

    def parse_string_to_dict(self, input_string):
        items = input_string.split(":")
        result = {}

        for i in range(0, len(items), 2):
            key = items[i]
            value = items[i + 1] if i + 1 < len(items) else ""
            result[key] = value

        return result

class LevelObject:
    def __init__(self, obj_string) -> None:
        self.properties = {}
        self.parse_object(obj_string)
    
    def parse_object(self, obj_string):
        pairs = obj_string.split(",")
        for i in range(0, len(pairs)-1, 2):
            try:
                key = int(pairs[i])
                value = pairs[i+1]

                try:
                    if "." in value:
                        self.properties[key] = float(value)
                    else:
                        self.properties[key] = int(value)
                except ValueError:
                    self.properties[key] = value
            except:
                continue

    def is_trigger(self):
        return self.properties[1] in TRIGGERS_IDS
                    
    def __str__(self):
        return f"Object ID: {self.properties.get(1, 'Unknown')}, Position: ({self.properties.get(2, '?')}, {self.properties.get(3, '?')}). Properties: ({self.properties})"

class GDLevel:
    def __init__(self, level_string, ignore_triggers=True) -> None:
        self.ignore_triggers = ignore_triggers
        self.headers = {}
        self.objects = []
        self.colors = {}
        self.version = self.detect_version(level_string)
        self.parse_level(level_string)
    
    def detect_version(self, level_string):
        if "kS38" in level_string:
            return "2.0+"
        elif "kS29" in level_string:
            return "1.9"
        else:
            return "1.0"
    
    def parse_colors_1_0(self):
        # В версии 1.0-1.811 цвета определяются через kS1-kS15
        color_groups = {
            "background": (1, 2, 3),
            "ground": (4, 5, 6),
            "line": (7, 8, 9),
            "object": (10, 11, 12),
            "player2": (13, 14, 15)
        }
        
        for name, (r_key, g_key, b_key) in color_groups.items():
            if f"kS{r_key}" in self.headers:
                self.colors[name] = {
                    "r": self.headers[f"kS{r_key}"],
                    "g": self.headers[f"kS{g_key}"],
                    "b": self.headers[f"kS{b_key}"],
                    "blending": False,
                    "opacity": 1.0
                }

    def parse_colors_2_0(self, color_string):
        # Парсинг цветов для версии 2.0+
        color_channels = color_string.split("|")
        for channel in color_channels:
            if not channel: continue
            
            properties = {}
            pairs = channel.split("_")
            for i in range(0, len(pairs)-1, 2):
                try:
                    properties[int(pairs[i])] = pairs[i+1]
                except:
                    continue
                    
            channel_id = int(properties.get(6, 0))
            self.colors[channel_id] = {
                "r": int(properties.get(1, 0)),
                "g": int(properties.get(2, 0)),
                "b": int(properties.get(3, 0)),
                "blending": bool(int(properties.get(5, 0))),
                "opacity": float(properties.get(7, 1)),
            }
    
    def parse_header_value(self, key, value):
        if key == "kS38" and self.version == "2.0+":
            self.parse_colors_2_0(value)
        else:
            try:
                self.headers[key] = float(value) if "." in value else int(value)
            except:
                self.headers[key] = value
    
    def parse_level(self, level_string):
        # Разделяем заголовок и объекты
        parts = level_string.split(";")
        if len(parts) < 2:
            return
        
        # Парсим заголовок
        header_parts = parts[0].split(",")
        for i in range(0, len(header_parts)-1, 2):
            try:
                key = header_parts[i]
                value = header_parts[i+1]
                self.parse_header_value(key, value)
            except:
                continue
        
        # Для версии 1.0 парсим цвета из kS параметров
        if self.version == "1.0":
            self.parse_colors_1_0()
        
        # Парсим объекты
        for obj_string in parts[1:-1]:
            if obj_string:
                level_object = LevelObject(obj_string)
                if self.ignore_triggers and level_object.is_trigger():
                    continue
                    
                self.objects.append(level_object)
    
    def __str__(self):
        version_str = f"GD Level (Version {self.version})\n"
        header_str = "Headers:\n" + "\n".join(f"  {k}: {v}" for k, v in self.headers.items())
        colors_str = "Colors:\n" + "\n".join(f"  Channel {k}: RGB({v['r']},{v['g']},{v['b']}) Blend:{v['blending']} Opacity:{v['opacity']}" for k, v in self.colors.items())
        objects_str = f"Objects ({len(self.objects)})"
        return f"{version_str}\n{header_str}\n\n{colors_str}\n\n{objects_str}"
