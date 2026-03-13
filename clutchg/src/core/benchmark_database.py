"""
Benchmark Database
Hardware benchmark scores for accurate system scoring
Based on PassMark data (normalized)
"""

from difflib import get_close_matches
from typing import Optional, Tuple

# CPU Benchmark Database
# Format: "CPU Name": (PassMark Score, Tier)
# Scores based on PassMark CPU Mark (2024-2025 data)
# Tier: 1=Entry, 2=Budget, 3=Mid, 4=High, 5=Enthusiast

CPU_DATABASE = {
    # AMD Ryzen 9000 Series (Latest)
    "AMD Ryzen 9 9950X": (65000, 5),
    "AMD Ryzen 9 9900X": (55000, 5),
    "AMD Ryzen 7 9700X": (42000, 5),
    "AMD Ryzen 5 9600X": (32000, 4),
    
    # AMD Ryzen 7000 Series
    "AMD Ryzen 9 7950X": (63000, 5),
    "AMD Ryzen 9 7950X3D": (60000, 5),
    "AMD Ryzen 9 7900X": (52000, 5),
    "AMD Ryzen 9 7900X3D": (51000, 5),
    "AMD Ryzen 7 7800X3D": (34500, 5),
    "AMD Ryzen 7 7700X": (36000, 5),
    "AMD Ryzen 7 7700": (33000, 4),
    "AMD Ryzen 5 7600X": (28500, 4),
    "AMD Ryzen 5 7600": (27000, 4),
    "AMD Ryzen 5 7500F": (26000, 4),
    
    # AMD Ryzen 5000 Series
    "AMD Ryzen 9 5950X": (46000, 5),
    "AMD Ryzen 9 5900X": (39000, 5),
    "AMD Ryzen 7 5800X": (28000, 4),
    "AMD Ryzen 7 5800X3D": (25500, 4),
    "AMD Ryzen 7 5700X": (26500, 4),
    "AMD Ryzen 7 5700G": (23000, 4),
    "AMD Ryzen 5 5600X": (22000, 4),
    "AMD Ryzen 5 5600": (21000, 4),
    "AMD Ryzen 5 5600G": (19500, 3),
    "AMD Ryzen 5 5500": (18500, 3),
    
    # AMD Ryzen 3000 Series
    "AMD Ryzen 9 3950X": (37000, 5),
    "AMD Ryzen 9 3900X": (32000, 4),
    "AMD Ryzen 7 3800X": (23000, 4),
    "AMD Ryzen 7 3700X": (22500, 4),
    "AMD Ryzen 5 3600": (17800, 3),
    "AMD Ryzen 5 3600X": (18000, 3),
    "AMD Ryzen 5 3500": (13000, 3),
    "AMD Ryzen 3 3300X": (13500, 3),
    "AMD Ryzen 3 3100": (12000, 2),
    
    # Intel 14th Gen (Raptor Lake Refresh)
    "Intel Core i9-14900K": (62000, 5),
    "Intel Core i9-14900KS": (65000, 5),
    "Intel Core i9-14900": (55000, 5),
    "Intel Core i7-14700K": (59000, 5),
    "Intel Core i7-14700": (48000, 5),
    "Intel Core i5-14600K": (41000, 5),
    "Intel Core i5-14600": (35000, 4),
    "Intel Core i5-14500": (32000, 4),
    "Intel Core i5-14400": (25000, 4),
    "Intel Core i3-14100": (14500, 3),
    
    # Intel 13th Gen (Raptor Lake)
    "Intel Core i9-13900K": (60000, 5),
    "Intel Core i9-13900KS": (62000, 5),
    "Intel Core i9-13900": (52000, 5),
    "Intel Core i7-13700K": (46000, 5),
    "Intel Core i7-13700": (38000, 5),
    "Intel Core i5-13600K": (38500, 5),
    "Intel Core i5-13600": (30000, 4),
    "Intel Core i5-13500": (28000, 4),
    "Intel Core i5-13400": (22000, 4),
    "Intel Core i3-13100": (13000, 3),
    
    # Intel 12th Gen (Alder Lake)
    "Intel Core i9-12900K": (41000, 5),
    "Intel Core i9-12900": (37000, 5),
    "Intel Core i7-12700K": (34500, 5),
    "Intel Core i7-12700": (31000, 4),
    "Intel Core i5-12600K": (27500, 4),
    "Intel Core i5-12600": (22000, 4),
    "Intel Core i5-12500": (19000, 4),
    "Intel Core i5-12400": (19500, 4),
    "Intel Core i3-12100": (14000, 3),
    
    # Intel 11th Gen (Rocket Lake)
    "Intel Core i9-11900K": (26000, 4),
    "Intel Core i7-11700K": (25000, 4),
    "Intel Core i7-11700": (23000, 4),
    "Intel Core i5-11600K": (21000, 4),
    "Intel Core i5-11400": (17500, 3),
    "Intel Core i3-11100": (10500, 2),
    
    # Intel 10th Gen (Comet Lake)
    "Intel Core i9-10900K": (24000, 4),
    "Intel Core i7-10700K": (20000, 4),
    "Intel Core i7-10700": (18500, 4),
    "Intel Core i5-10600K": (15000, 3),
    "Intel Core i5-10400": (13000, 3),
    "Intel Core i3-10100": (8500, 2),
    
    # Budget/Entry CPUs
    "Intel Pentium Gold G7400": (5500, 1),
    "Intel Celeron G6900": (3500, 1),
    "AMD Athlon 3000G": (5000, 1),
    "AMD Ryzen 3 3200G": (7500, 2),
    
    # Laptop CPUs (Common)
    "AMD Ryzen 9 7945HX": (55000, 5),
    "AMD Ryzen 7 7840HS": (30000, 4),
    "AMD Ryzen 7 6800H": (24000, 4),
    "AMD Ryzen 5 7535HS": (20000, 4),
    "AMD Ryzen 5 6600H": (18000, 3),
    "Intel Core i9-13980HX": (45000, 5),
    "Intel Core i7-13700H": (28000, 4),
    "Intel Core i5-13500H": (22000, 4),
    "Intel Core i7-12700H": (27000, 4),
    "Intel Core i5-12500H": (20000, 4),
}

# GPU Benchmark Database  
# Format: "GPU Name": (G3D Mark Score, VRAM GB, Tier)
# Scores based on PassMark G3D Mark (2024-2025 data)

GPU_DATABASE = {
    # NVIDIA RTX 50 Series (Latest)
    "NVIDIA GeForce RTX 5090": (55000, 32, 5),
    "NVIDIA GeForce RTX 5080": (42000, 16, 5),
    "NVIDIA GeForce RTX 5070 Ti": (35000, 16, 5),
    "NVIDIA GeForce RTX 5070": (30000, 12, 5),
    "NVIDIA GeForce RTX 5060 Ti": (25000, 16, 4),
    "NVIDIA GeForce RTX 5060": (20000, 8, 4),
    
    # NVIDIA RTX 40 Series
    "NVIDIA GeForce RTX 4090": (39000, 24, 5),
    "NVIDIA GeForce RTX 4080 SUPER": (35000, 16, 5),
    "NVIDIA GeForce RTX 4080": (34000, 16, 5),
    "NVIDIA GeForce RTX 4070 Ti SUPER": (31000, 16, 5),
    "NVIDIA GeForce RTX 4070 Ti": (29000, 12, 5),
    "NVIDIA GeForce RTX 4070 SUPER": (27000, 12, 5),
    "NVIDIA GeForce RTX 4070": (23500, 12, 4),
    "NVIDIA GeForce RTX 4060 Ti": (22000, 16, 4),
    "NVIDIA GeForce RTX 4060": (19000, 8, 4),
    
    # NVIDIA RTX 30 Series
    "NVIDIA GeForce RTX 3090 Ti": (29500, 24, 5),
    "NVIDIA GeForce RTX 3090": (26500, 24, 5),
    "NVIDIA GeForce RTX 3080 Ti": (27000, 12, 5),
    "NVIDIA GeForce RTX 3080": (25000, 10, 5),
    "NVIDIA GeForce RTX 3070 Ti": (22500, 8, 4),
    "NVIDIA GeForce RTX 3070": (21500, 8, 4),
    "NVIDIA GeForce RTX 3060 Ti": (19500, 8, 4),
    "NVIDIA GeForce RTX 3060": (17000, 12, 4),
    "NVIDIA GeForce RTX 3050": (12500, 8, 3),
    
    # NVIDIA RTX 20 Series
    "NVIDIA GeForce RTX 2080 Ti": (21500, 11, 4),
    "NVIDIA GeForce RTX 2080 SUPER": (19000, 8, 4),
    "NVIDIA GeForce RTX 2080": (17500, 8, 4),
    "NVIDIA GeForce RTX 2070 SUPER": (17000, 8, 4),
    "NVIDIA GeForce RTX 2070": (15500, 8, 4),
    "NVIDIA GeForce RTX 2060 SUPER": (15000, 8, 4),
    "NVIDIA GeForce RTX 2060": (13500, 6, 3),
    
    # NVIDIA GTX 16 Series
    "NVIDIA GeForce GTX 1660 Ti": (11500, 6, 3),
    "NVIDIA GeForce GTX 1660 SUPER": (12000, 6, 3),
    "NVIDIA GeForce GTX 1660": (10500, 6, 3),
    "NVIDIA GeForce GTX 1650 SUPER": (9500, 4, 3),
    "NVIDIA GeForce GTX 1650": (7500, 4, 2),
    
    # NVIDIA GTX 10 Series
    "NVIDIA GeForce GTX 1080 Ti": (16500, 11, 4),
    "NVIDIA GeForce GTX 1080": (14000, 8, 4),
    "NVIDIA GeForce GTX 1070 Ti": (13000, 8, 3),
    "NVIDIA GeForce GTX 1070": (12500, 8, 3),
    "NVIDIA GeForce GTX 1060 6GB": (9500, 6, 3),
    "NVIDIA GeForce GTX 1060 3GB": (9000, 3, 3),
    "NVIDIA GeForce GTX 1050 Ti": (6500, 4, 2),
    "NVIDIA GeForce GTX 1050": (5000, 2, 2),
    
    # AMD Radeon RX 7000 Series
    "AMD Radeon RX 7900 XTX": (33000, 24, 5),
    "AMD Radeon RX 7900 XT": (28000, 20, 5),
    "AMD Radeon RX 7900 GRE": (25000, 16, 5),
    "AMD Radeon RX 7800 XT": (23000, 16, 4),
    "AMD Radeon RX 7700 XT": (20000, 12, 4),
    "AMD Radeon RX 7600 XT": (16000, 16, 4),
    "AMD Radeon RX 7600": (14500, 8, 4),
    
    # AMD Radeon RX 6000 Series
    "AMD Radeon RX 6950 XT": (27000, 16, 5),
    "AMD Radeon RX 6900 XT": (25000, 16, 5),
    "AMD Radeon RX 6800 XT": (24000, 16, 5),
    "AMD Radeon RX 6800": (21500, 16, 4),
    "AMD Radeon RX 6750 XT": (18500, 12, 4),
    "AMD Radeon RX 6700 XT": (17500, 12, 4),
    "AMD Radeon RX 6650 XT": (15000, 8, 4),
    "AMD Radeon RX 6600 XT": (14500, 8, 4),
    "AMD Radeon RX 6600": (13000, 8, 3),
    "AMD Radeon RX 6500 XT": (7500, 4, 2),
    "AMD Radeon RX 6400": (5500, 4, 2),
    
    # AMD Radeon RX 5000 Series
    "AMD Radeon RX 5700 XT": (15500, 8, 4),
    "AMD Radeon RX 5700": (14000, 8, 4),
    "AMD Radeon RX 5600 XT": (12500, 6, 3),
    "AMD Radeon RX 5500 XT": (8500, 8, 3),
    
    # Intel Arc
    "Intel Arc A770": (17000, 16, 4),
    "Intel Arc A750": (15000, 8, 4),
    "Intel Arc A580": (12000, 8, 3),
    "Intel Arc A380": (6500, 6, 2),
    
    # Integrated Graphics
    "AMD Radeon Graphics (Ryzen 7000)": (3500, 0, 1),
    "AMD Radeon Vega 8": (2500, 0, 1),
    "AMD Radeon Vega 7": (2200, 0, 1),
    "Intel UHD Graphics 770": (2000, 0, 1),
    "Intel UHD Graphics 730": (1500, 0, 1),
    "Intel UHD Graphics 630": (1500, 0, 1),
}


class BenchmarkDatabase:
    """Hardware benchmark score database with fuzzy matching"""
    
    # Score ranges for normalization
    CPU_MAX_SCORE = 65000  # Top CPU score
    GPU_MAX_SCORE = 55000  # Top GPU score
    
    def __init__(self):
        self.cpu_data = CPU_DATABASE
        self.gpu_data = GPU_DATABASE
    
    def get_cpu_score(self, cpu_name: str) -> Tuple[int, int, str]:
        """
        Get CPU benchmark score
        
        Args:
            cpu_name: CPU name to lookup
            
        Returns:
            Tuple of (normalized_score 0-30, raw_score, matched_name)
        """
        matched_name = self._fuzzy_match(cpu_name, list(self.cpu_data.keys()))
        
        if matched_name:
            raw_score, tier = self.cpu_data[matched_name]
            # Normalize to 0-30 scale
            normalized = min(30, int((raw_score / self.CPU_MAX_SCORE) * 30))
            return (normalized, raw_score, matched_name)
        
        # Default fallback based on cores (old method)
        return (15, 0, "Unknown CPU")
    
    def get_gpu_score(self, gpu_name: str) -> Tuple[int, int, int, str]:
        """
        Get GPU benchmark score
        
        Args:
            gpu_name: GPU name to lookup
            
        Returns:
            Tuple of (normalized_score 0-30, raw_score, vram_gb, matched_name)
        """
        matched_name = self._fuzzy_match(gpu_name, list(self.gpu_data.keys()))
        
        if matched_name:
            raw_score, vram, tier = self.gpu_data[matched_name]
            # Normalize to 0-30 scale
            normalized = min(30, int((raw_score / self.GPU_MAX_SCORE) * 30))
            return (normalized, raw_score, vram, matched_name)
        
        # Default fallback
        return (10, 0, 0, "Unknown GPU")
    
    def _fuzzy_match(self, query: str, options: list, cutoff: float = 0.5) -> Optional[str]:
        """
        Fuzzy match a query string to options
        
        Args:
            query: String to match
            options: List of possible matches
            cutoff: Minimum similarity score (0-1)
            
        Returns:
            Best matching option or None
        """
        if not query:
            return None
            
        # Clean query
        query_clean = query.lower().strip()
        
        # Try exact match first
        for opt in options:
            if query_clean == opt.lower():
                return opt
        
        # Try contains match
        for opt in options:
            opt_lower = opt.lower()
            # Check if key parts match
            if self._key_parts_match(query_clean, opt_lower):
                return opt
        
        # Fuzzy match as last resort
        matches = get_close_matches(query_clean, [o.lower() for o in options], n=1, cutoff=cutoff)
        if matches:
            # Find original case version
            for opt in options:
                if opt.lower() == matches[0]:
                    return opt
        
        return None
    
    def _key_parts_match(self, query: str, option: str) -> bool:
        """Check if key parts of hardware name match"""
        # Extract key identifiers
        # For CPUs: model number like "7800x3d", "14900k", "5600x"  
        # For GPUs: model number like "5060", "4090", "7900 xtx"
        
        import re
        
        # Find model numbers (digits + optional letters)
        query_models = re.findall(r'\d{4}[a-z0-9]*', query)
        option_models = re.findall(r'\d{4}[a-z0-9]*', option)
        
        # Check for matching model numbers
        for qm in query_models:
            for om in option_models:
                if qm in om or om in qm:
                    # Also check vendor match
                    if ('amd' in query and 'amd' in option) or \
                       ('intel' in query and 'intel' in option) or \
                       ('nvidia' in query and 'nvidia' in option) or \
                       ('geforce' in query and 'geforce' in option) or \
                       ('radeon' in query and 'radeon' in option) or \
                       ('ryzen' in query and 'ryzen' in option):
                        return True
        
        return False
    
    def get_tier_name(self, tier: int) -> str:
        """Convert tier number to name"""
        tiers = {1: "Entry", 2: "Budget", 3: "Mid", 4: "High", 5: "Enthusiast"}
        return tiers.get(tier, "Unknown")


# Singleton instance
_benchmark_db = None

def get_benchmark_db() -> BenchmarkDatabase:
    """Get singleton benchmark database instance"""
    global _benchmark_db
    if _benchmark_db is None:
        _benchmark_db = BenchmarkDatabase()
    return _benchmark_db


if __name__ == "__main__":
    # Test the database
    db = BenchmarkDatabase()
    
    # Test CPU matching
    test_cpus = [
        "AMD Ryzen 7 7800X3D 8-Core Processor",
        "Intel Core i7-14700K",
        "AMD Ryzen 5 5600X",
        "Intel Core i5-12400",
    ]
    
    print("=== CPU Benchmark Scores ===")
    for cpu in test_cpus:
        score, raw, matched = db.get_cpu_score(cpu)
        print(f"{cpu}")
        print(f"  Matched: {matched}")
        print(f"  Raw Score: {raw:,}")
        print(f"  Normalized (0-30): {score}")
        print()
    
    # Test GPU matching
    test_gpus = [
        "NVIDIA GeForce RTX 5060",
        "NVIDIA GeForce RTX 4090",
        "AMD Radeon RX 7900 XTX",
        "NVIDIA GeForce GTX 1660 SUPER",
    ]
    
    print("=== GPU Benchmark Scores ===")
    for gpu in test_gpus:
        score, raw, vram, matched = db.get_gpu_score(gpu)
        print(f"{gpu}")
        print(f"  Matched: {matched}")
        print(f"  Raw Score: {raw:,}")
        print(f"  VRAM: {vram}GB")
        print(f"  Normalized (0-30): {score}")
        print()
