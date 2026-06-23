import pandas as pd


class HardwareScoringEngine:
    def __init__(self, max_gpu_score: float = 30000.0, max_cpu_score: float = 45000.0):
        self.max_gpu_score = max_gpu_score
        self.max_cpu_score = max_cpu_score

    def normalize_gpu(self, raw_score: float) -> float:
        return min((max(raw_score, 1.0) / self.max_gpu_score) * 100.0, 100.0)

    def normalize_cpu(self, raw_score: float) -> float:
        return min((max(raw_score, 1.0) / self.max_cpu_score) * 100.0, 100.0)

    def calculate_ram_score(self, capacity_gb: float) -> float:
        if capacity_gb <= 4: return 20.0
        if capacity_gb <= 8: return 50.0
        if capacity_gb <= 16: return 85.0
        return 100.0

    def calculate_vram_score(self, vram_gb: float) -> float:
        if vram_gb <= 2: return 20.0
        if vram_gb <= 4: return 45.0
        if vram_gb <= 8: return 80.0
        if vram_gb <= 12: return 95.0
        return 100.0


class CompatibilityEngine:
    def __init__(self, sql_conn, scorer: HardwareScoringEngine):
        self.sql_conn = sql_conn
        self.scorer = scorer
        self.weights = {"gpu": 0.45, "cpu": 0.30, "ram": 0.15, "vram": 0.10}

    def evaluate(self, target_title: str, user_build: dict) -> dict:
        query = """
                SELECT g.GAME_ID, \
                       c_min.MODEL as MIN_CPU_M, \
                       g_min.MODEL as MIN_GPU_M, \
                       r_min.Capacity_GB as MIN_RAM, \
                       g_min.VRAM_GB as MIN_VRAM, \
                       c_rec.MODEL as REC_CPU_M, \
                       g_rec.MODEL as REC_GPU_M, \
                       r_rec.Capacity_GB as REC_RAM, \
                       g_rec.VRAM_GB as REC_VRAM, \
                       c_min.BENCHMARK_SCORE as MIN_CPU_SCORE, \
                       g_min.BENCHMARK_SCORE as MIN_GPU_SCORE, \
                       c_rec.BENCHMARK_SCORE as REC_CPU_SCORE, \
                       g_rec.BENCHMARK_SCORE as REC_GPU_SCORE, \
                       CASE \
                           WHEN :u_ram < r_min.Capacity_GB OR :u_vram < g_min.VRAM_GB THEN 'BELOW MINIMUM' \
                           WHEN :u_cpu < c_min.BENCHMARK_SCORE OR :u_gpu < g_min.BENCHMARK_SCORE THEN 'BELOW MINIMUM' \
                           WHEN :u_ram >= r_rec.Capacity_GB AND :u_vram >= g_rec.VRAM_GB AND \
                                :u_cpu >= c_rec.BENCHMARK_SCORE AND :u_gpu >= g_rec.BENCHMARK_SCORE THEN 'ULTRA READY' \
                           WHEN :u_ram >= r_rec.Capacity_GB AND :u_cpu >= (c_rec.BENCHMARK_SCORE * 0.8) AND \
                                :u_gpu >= (g_rec.BENCHMARK_SCORE * 0.8) THEN 'RECOMMENDED READY' \
                           ELSE 'MINIMUM READY' \
                           END AS DB_STATUS, \
                       CASE WHEN :u_ram < r_min.Capacity_GB THEN 1 ELSE 0 END AS FAIL_RAM, \
                       CASE WHEN :u_vram < g_min.VRAM_GB THEN 1 ELSE 0 END AS FAIL_VRAM, \
                       CASE WHEN :u_cpu < c_min.BENCHMARK_SCORE THEN 1 ELSE 0 END AS FAIL_CPU, \
                       CASE WHEN :u_gpu < g_min.BENCHMARK_SCORE THEN 1 ELSE 0 END AS FAIL_GPU
                FROM GAMES g
                         JOIN GAME_REQUIREMENTS req_min ON g.GAME_ID = req_min.Game_ID AND req_min.Req_Type = 'MIN'
                         JOIN CPUS c_min ON req_min.CPU_ID = c_min.CPU_ID
                         JOIN GPUS g_min ON req_min.GPU_ID = g_min.GPU_ID
                         JOIN RAM_CONFIGURATIONS r_min ON req_min.RAM_ID = r_min.RAM_ID
                         JOIN GAME_REQUIREMENTS req_rec ON g.GAME_ID = req_rec.Game_ID AND req_rec.Req_Type = 'REC'
                         JOIN CPUS c_rec ON req_rec.CPU_ID = c_rec.CPU_ID
                         JOIN GPUS g_rec ON req_rec.GPU_ID = g_rec.GPU_ID
                         JOIN RAM_CONFIGURATIONS r_rec ON req_rec.RAM_ID = r_rec.RAM_ID
                WHERE g.TITLE = :title \
                """

        df = pd.read_sql(query, con=self.sql_conn, params={
            "u_ram": user_build["ram_capacity"], "u_vram": user_build["vram_gb"],
            "u_cpu": user_build["cpu_score"], "u_gpu": user_build["gpu_score"],
            "title": target_title
        })

        if df.empty:
            raise ValueError(f"Target '{target_title}' requirements not found in Database.")

        row = df.iloc[0]
        status = row["DB_STATUS"]
        checks = {"ram_failed_min": bool(row["FAIL_RAM"]), "vram_failed_min": bool(row["FAIL_VRAM"]),
                  "cpu_failed_min": bool(row["FAIL_CPU"]), "gpu_failed_min": bool(row["FAIL_GPU"])}

        s_gpu = self.scorer.normalize_gpu(user_build["gpu_score"])
        s_cpu = self.scorer.normalize_cpu(user_build["cpu_score"])
        s_ram = self.scorer.calculate_ram_score(user_build["ram_capacity"])
        s_vram = self.scorer.calculate_vram_score(user_build["vram_gb"])

        p_gate = 1.0
        if checks["ram_failed_min"]: p_gate *= 0.40
        if checks["vram_failed_min"]: p_gate *= 0.35
        if checks["cpu_failed_min"] or checks["gpu_failed_min"]: p_gate *= 0.60

        composite_score = (self.weights["gpu"] * s_gpu + self.weights["cpu"] * s_cpu + self.weights["ram"] * s_ram +
                           self.weights["vram"] * s_vram) * p_gate

        return {
            "composite_score": round(composite_score, 2), "status_level": status, "failed_checks": checks,
            "component_scores": {"gpu": s_gpu, "cpu": s_cpu, "ram": s_ram, "vram": s_vram},
            "game_req": {
                "game_id": int(row["GAME_ID"]),
                "min_cpu_m": row["MIN_CPU_M"], "min_gpu_m": row["MIN_GPU_M"], "min_ram": float(row["MIN_RAM"]),
                "min_vram": float(row["MIN_VRAM"]),
                "rec_cpu_m": row["REC_CPU_M"], "rec_gpu_m": row["REC_GPU_M"], "rec_ram": float(row["REC_RAM"]),
                "rec_vram": float(row["REC_VRAM"]),
                "rec_cpu_score": float(row["REC_CPU_SCORE"]), "rec_gpu_score": float(row["REC_GPU_SCORE"])
            }
        }


class FPSPredictionEngine:
    def __init__(self):
        self.resolution_modifiers = {"1080p": 1.0, "1440p": 0.72, "4K": 0.42}
        self.preset_modifiers = {"Low": 1.45, "Medium": 1.20, "High": 1.0, "Ultra": 0.78}

    def predict(self, telemetry_data: list, user_build: dict, target_res: str, target_preset: str) -> dict:
        matching_logs = [log for log in telemetry_data if
                         log.get("game_settings", {}).get("resolution") == target_res and log.get("game_settings",
                                                                                                  {}).get(
                             "graphics_preset") == target_preset]

        if matching_logs:
            base_fps = sum(log["performance_metrics"]["fps"]["average_fps"] for log in matching_logs) / len(
                matching_logs)
            min_fps = sum(log["performance_metrics"]["fps"]["one_percent_low"] for log in matching_logs) / len(
                matching_logs)
            confidence = "HIGH (Direct Telemetry Match)"
        else:
            global_logs = [log for log in telemetry_data if
                           log.get("performance_metrics", {}).get("fps", {}).get("average_fps", 0) > 0]
            if not global_logs:
                base_fps = (user_build["gpu_score"] / 220.0) * self.resolution_modifiers[target_res] * \
                           self.preset_modifiers[target_preset]
                min_fps = base_fps * 0.72
                confidence = "LOW (Algorithmic Estimation)"
            else:
                pivot_fps = sum(log["performance_metrics"]["fps"]["average_fps"] for log in global_logs) / len(
                    global_logs)
                base_fps = pivot_fps * self.resolution_modifiers[target_res] * self.preset_modifiers[target_preset]
                min_fps = base_fps * 0.75
                confidence = "MEDIUM (Heuristic Interpolation)"

        if user_build["ram_capacity"] < 12.0:
            base_fps *= 0.75
            min_fps *= 0.50
        if user_build["vram_gb"] < 6.0 and target_res in ["1440p", "4K"]:
            base_fps *= 0.65
            min_fps *= 0.45

        return {"avg_fps": max(int(base_fps), 1), "min_fps": max(int(min_fps), 1), "confidence": confidence}


class UpgradeRecommendationEngine:
    def __init__(self, predictor: FPSPredictionEngine):
        self.predictor = predictor

    def find_optimal_settings(self, telemetry_data: list, user_build: dict) -> dict:
        for res in ["4K", "1440p", "1080p"]:
            for preset in ["Ultra", "High", "Medium", "Low"]:
                perf = self.predictor.predict(telemetry_data, user_build, res, preset)
                if perf["avg_fps"] >= 60:
                    return {"resolution": res, "preset": preset, "avg_fps": perf["avg_fps"]}
        return {"resolution": "1080p", "preset": "Low", "avg_fps": 30}

    def generate_upgrades(self, user_build: dict, game_req: dict) -> list:
        upgrades = []
        if user_build["ram_capacity"] < game_req["rec_ram"]:
            upgrades.append({"component": "System RAM",
                             "issue": f"RAM capacity ({user_build['ram_capacity']}GB) is below recommended limits ({game_req['rec_ram']}GB).",
                             "fix": "Install an additional matching memory module to stabilize frame times."})
        if user_build["gpu_score"] < game_req["rec_gpu_score"]:
            upgrades.append({"component": "Graphics Card (GPU)",
                             "issue": "GPU compute index is below optimal targets for high fidelity assets.",
                             "fix": "Upgrade to a graphics card with greater microarchitecture rendering capability."})
        if user_build["cpu_score"] < user_build["gpu_score"] * 0.72:
            upgrades.append({"component": "Processor (CPU)",
                             "issue": "CPU processing delay is bottlenecking GPU throughput limits.",
                             "fix": "Upgrade to a higher core count processor to clear pipeline queues."})
        return upgrades