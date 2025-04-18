import asyncio
import os
import signal
import time
from typing import List, Set

import macrocosmos as mc
from macrocosmos.generated.gravity.v1 import gravity_pb2

from pathlib import Path
from dotenv import load_dotenv
BASE_DIR = Path(__file__).resolve().parent.parent  
load_dotenv(os.path.join(BASE_DIR, '.env'))

class GravityWorkflow:
    def __init__(self, task_name: str, email: str, reddit_subreddit: str, x_hashtag: str):
        self.task_name = task_name
        self.email = email
        self.reddit_subreddit = reddit_subreddit
        self.x_hashtag = x_hashtag
        self.api_key = os.environ.get(os.environ.get("MACROCOSMOS_API_KEY"))
        self.client = mc.AsyncGravityClient(
            max_retries=1,
            timeout=30,
            api_key=self.api_key,
            app_name="examples/gravity_workflow_example",
        )
        self.task_id = None
        self.crawler_ids = []
        self.dataset_ids = []

    async def run(self):
        """Run the complete Gravity workflow."""
        try:
            # Step 1: Check for existing tasks and cancel them if necessary.
            await self.find_and_cancel_existing_task()

            # Step 2: Create a new task with the specified crawlers.
            await self.create_new_task()

            if not self.task_id:
                print("Failed to create task. Exiting.")
                return

            # Step 3: Monitor crawler data collection progress for 60 seconds.
            crawlers_with_data = await self.monitor_data_collection()

            # Step 4: For crawlers that collected data, build datasets.
            if crawlers_with_data:
                await self.build_datasets(crawlers_with_data)

                # Step 5: Monitor the dataset build progress and display details.
                if self.dataset_ids:
                    await self.monitor_dataset_builds()

                    # Step 6: Wait for user input before cleanup.
                    print(
                        "\n📌 Press Enter when you're done downloading the datasets to clean up and exit..."
                    )
                    await self.wait_for_input()
            else:
                print("\n⚠️ No crawlers collected data within the time limit.")
                await self.cleanup(self.task_id)

        except (KeyboardInterrupt, asyncio.CancelledError):
            print("\n⚠️ Operation canceled.")
            await self.cleanup(self.task_id)
        except Exception as e:
            print(f"\n❌ Error in workflow: {e}")
            await self.cleanup(self.task_id)
            raise

    async def find_and_cancel_existing_task(self):
        """Check for existing tasks with the same name and cancel any that are not completed."""
        print(f"\n🔍 Checking if tasks with name '{self.task_name}' exist...")

        try:
            response = await self.client.gravity.GetGravityTasks(include_crawlers=False)
            existing_tasks: List[gravity_pb2.GravityTaskState] = []
            if response and response.gravity_task_states:
                for task in response.gravity_task_states:
                    if task.name == self.task_name:
                        existing_tasks.append(task)

            if existing_tasks:
                print(f" Found {len(existing_tasks)} tasks with name '{self.task_name}'")

                tasks_to_cancel = [task for task in existing_tasks if task.status != "Completed"]
                if tasks_to_cancel:
                    print(f" Cancelling {len(tasks_to_cancel)} non-completed tasks...")
                    for task in tasks_to_cancel:
                        await self.cleanup(task.gravity_task_id)
                    print("✅ All non-completed tasks cancelled successfully.")
                    await asyncio.sleep(3)
                else:
                    print("✅ All existing tasks are already completed.")
            else:
                print(f"✅ No existing tasks named '{self.task_name}' found.")

        except Exception as e:
            print(f"❌ Error checking/cancelling existing tasks: {e}")
            raise

    async def create_new_task(self):
        """Create a new Gravity task with X and Reddit crawlers."""
        print(f"\n🔨 Creating new task '{self.task_name}'...")

        try:
            gravity_tasks = [
                {"topic": self.x_hashtag, "platform": "x"},
                {"topic": self.reddit_subreddit, "platform": "reddit"},
            ]

            notification = {
                "type": "email",
                "address": self.email,
                "redirect_url": "https://app.macrocosmos.ai/",
            }

            response = await self.client.gravity.CreateGravityTask(
                gravity_tasks=gravity_tasks,
                name=self.task_name,
                notification_requests=[notification],
            )

            self.task_id = response.gravity_task_id
            print(f"✅ Task created successfully with ID: {self.task_id}")
            await asyncio.sleep(10)

        except Exception as e:
            print(f"❌ Error creating new task: {e}")
            raise

    async def monitor_data_collection(self) -> Set[str]:
        """Monitor crawler data collection for 60 seconds and return the set of crawler IDs that have collected data."""
        print("\n⏱️ Monitoring data collection for 60 seconds...")

        crawlers_with_data = set()
        start_time = time.time()
        end_time = start_time + 60

        try:
            response = await self.client.gravity.GetGravityTasks(
                gravity_task_id=self.task_id, include_crawlers=False
            )
            if response and response.gravity_task_states:
                task = response.gravity_task_states[0]
                self.crawler_ids = list(task.crawler_ids)
            else:
                print("❌ Gravity task response is empty")
                return crawlers_with_data
        except Exception as e:
            print(f"❌ Error getting crawler IDs: {e}")
            return crawlers_with_data

        print("\n{:<12} {:<25} {:<15} {:<15}".format("TIME", "CRAWLER", "STATUS", "RECORDS"))
        print("─" * 70)
        num_status_lines = len(self.crawler_ids)

        while time.time() < end_time:
            elapsed = time.time() - start_time
            try:
                print(f"\033[{num_status_lines}A", end="")
                for crawler_id in self.crawler_ids:
                    resp = await self.client.gravity.GetCrawler(crawler_id=crawler_id)
                    crawler = resp.crawler
                    if crawler.state.records_collected > 0:
                        crawlers_with_data.add(crawler.crawler_id)

                    status = crawler.state.status
                    indicator = "⏳" if status == "Pending" else "🟢" if status == "Running" else "✅" if status == "Completed" else "❌"
                    records_disp = f"{crawler.state.records_collected} ↑" if crawler.state.records_collected > 0 else "0"

                    print("{:<12} {:<25} {:<15} {:<15}".format(
                        f"{elapsed:.1f}s",
                        f"{crawler.criteria.platform}/{crawler.criteria.topic}",
                        f"{indicator} {status}",
                        records_disp,
                    ))
                await asyncio.sleep(10)
            except Exception as e:
                print(f"❌ Error monitoring task: {e}")

        print(f"\n✅ Monitoring complete. Found {len(crawlers_with_data)} crawlers with data.")
        return crawlers_with_data

    async def wait_for_completion(self, crawler_id: str, poll_interval: float = 5, timeout: float = 300):
        """Poll until a crawler has fully completed fetching data, with a timeout."""
        print(f"⏳ Waiting for crawler {crawler_id} to reach 'Completed' status (timeout={timeout}s)...")
        deadline = time.time() + timeout
        while time.time() < deadline:
            resp = await self.client.gravity.GetCrawler(crawler_id=crawler_id)
            status = resp.crawler.state.status
            if status == "Completed":
                print(f"✅ Crawler {crawler_id} completed.")
                return
            if status in ("Failed", "Cancelled"):
                raise RuntimeError(f"Crawler {crawler_id} ended with status={status}")
            await asyncio.sleep(poll_interval)
        raise asyncio.TimeoutError(f"Timed out waiting for crawler {crawler_id} after {timeout}s")

    async def build_datasets(self, crawler_ids: Set[str]):
        """Trigger dataset builds, waiting up to a timeout for each crawler to complete."""
        print(f"📦 Building datasets for {len(crawler_ids)} crawlers...")

        notification = {
            "type": "email",
            "address": self.email,
            "redirect_url": "https://app.macrocosmos.ai/gravity/tasks",
        }

        for crawler_id in crawler_ids:
            try:
                # Wait for completion up to timeout
                await self.wait_for_completion(crawler_id)
            except asyncio.TimeoutError as te:
                print(f"⚠️ {te}. Proceeding to build dataset for {crawler_id} anyway.")
            except Exception as e:
                print(f"❌ Aborting dataset build for {crawler_id}: {e}")
                continue

            try:
                response = await self.client.gravity.BuildDataset(
                    crawler_id=crawler_id, notification_requests=[notification]
                )

                if response and response.dataset_id:
                    self.dataset_ids.append(response.dataset_id)
                    print(f"✅ Dataset build initiated for crawler {crawler_id} (dataset={response.dataset_id})")
                else:
                    print(f"❌ Failed to initiate dataset build for crawler {crawler_id}")

            except Exception as e:
                print(f"❌ Error building dataset for crawler {crawler_id}: {e}")
                raise

    async def monitor_dataset_builds(self, crawler_ids: Set[str]):
        """Trigger dataset builds, waiting up to a timeout for each crawler to complete."""
        print(f"\n📦 Building datasets for {len(crawler_ids)} crawlers...")

        notification = {
            "type": "email",
            "address": self.email,
            "redirect_url": "https://app.macrocosmos.ai/gravity/tasks",
        }

        for crawler_id in crawler_ids:
            try:
                # Wait for completion, but don't hang forever
                await self.wait_for_completion(crawler_id)
            except asyncio.TimeoutError as te:
                print(f"⚠️ {te}. Proceeding to build dataset for {crawler_id} anyway.")
            except Exception as e:
                print(f"❌ Aborting dataset build for {crawler_id}: {e}")
                continue

            try:
                resp = await self.client.gravity.BuildDataset(
                    crawler_id=crawler_id,
                    notification_requests=[notification]
                )
                if resp and resp.dataset_id:
                    self.dataset_ids.append(resp.dataset_id)
                    print(f"✅ Dataset build initiated for crawler {crawler_id} (dataset={resp.dataset_id})")
                else:
                    print(f"❌ Failed to initiate dataset build for crawler {crawler_id}")
            except Exception as e:
                print(f"❌ Error building dataset for crawler {crawler_id}: {e}")
                raise

    async def monitor_dataset_builds(self):
        """Monitor dataset builds and display status until all are complete."""
        print(f"\n⏱️ Monitoring {len(self.dataset_ids)} dataset builds...")
        completed = set()
        status_map = {}
        start_time = time.time()

        print("\n{:<10} {:<25} {:<16} {:<12} {:<10} {:<30}".format("TIME","DATASET","STATUS","STEP","PROGRESS","MESSAGE"))
        print("─"*110)
        num_lines = len(self.dataset_ids)

        while len(completed) < len(self.dataset_ids):
            if int(time.time() - start_time) % 5 == 0:
                for ds_id in self.dataset_ids:
                    if ds_id in completed: continue
                    try:
                        resp = await self.client.gravity.GetDataset(dataset_id=ds_id)
                        ds = resp.dataset
                        current = ds.steps[-1] if ds.steps else None
                        step_info = f"Step {current.step}/{ds.total_steps}" if current else ""
                        pct = f"{(current.progress*100):.1f}%" if current else ""
                        indicator = "✅" if ds.status=="Completed" else "❌" if ds.status in ("Failed","Cancelled") else "⏳"
                        status_map[ds_id] = (indicator + " " + ds.status, step_info, pct, ds.status_message or "")
                        if ds.status in ("Completed","Failed","Cancelled"): completed.add(ds_id)
                    except Exception as e:
                        status_map[ds_id] = ("❌ Error","","",""+str(e))

            elapsed = time.time()-start_time
            print(f"\033[{num_lines}A", end="")
            for ds_id in self.dataset_ids:
                stat = status_map.get(ds_id, ("","","",""))
                short = (ds_id[:21]+"...") if len(ds_id)>24 else ds_id
                msg = (stat[3][:27]+"...") if len(stat[3])>30 else stat[3]
                print("{:<10} {:<25} {:<16} {:<12} {:<10} {:<30}".format(f"{elapsed:.1f}s", short, stat[0], stat[1], stat[2], msg))

            await asyncio.sleep(10)

        # Show files
        for ds_id in self.dataset_ids:
            info = status_map.get(ds_id)
            if info and "Completed" in info[0]:
                ds = (await self.client.gravity.GetDataset(dataset_id=ds_id)).dataset
                if ds.files:
                    print(f"\n📄 Dataset {ds_id} files:")
                    for i,f in enumerate(ds.files,1):
                        size_mb = f.file_size_bytes/(1024*1024)
                        print(f"   File {i}: {f.file_name} ({size_mb:.2f}MB, {f.num_rows} rows) URL: {f.url}")
        print("\n✅ All dataset builds completed!")

    async def wait_for_input(self):
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, input)
        await self.cleanup(self.task_id)

    async def cleanup(self, task_id: str):
        print("\n🧹 Cleaning up:")
        if task_id:
            try:
                print(f"  • Cancelling gravity task {task_id}...")
                await self.client.gravity.CancelGravityTask(gravity_task_id=task_id)
            except Exception as e:
                print(f"❌ Error cancelling task: {e}")
        for ds_id in self.dataset_ids:
            try:
                print(f"  • Cancelling dataset {ds_id}...")
                await self.client.gravity.CancelDataset(dataset_id=ds_id)
            except:
                pass

def get_user_input():
    print("\n📝 Please enter your preferences (press Enter for defaults):")
    email = input("Email address [your@email.com]: ").strip() or "your@email.com"
    reddit = input("Reddit subreddit [r/MachineLearning]: ").strip() or "r/MachineLearning"
    if not reddit.startswith("r/"): reddit = f"r/{reddit}"
    x_hashtag = input("X hashtag [#ai]: ").strip() or "#ai"
    if not x_hashtag.startswith("#"): x_hashtag = f"#{x_hashtag}"
    task_name = input("Task name [MyTestTask]: ").strip() or "MyTestTask"
    return email, reddit, x_hashtag, task_name

async def handle_signal(workflow):
    for task in asyncio.all_tasks():
        if task is not asyncio.current_task(): task.cancel()

async def main():
    print("════════════════════════════════════════════════════")
    print("          🚀 Gravity Workflow Example")
    print("════════════════════════════════════════════════════")

   

    email, reddit, x_hashtag, task_name = get_user_input()
    workflow = GravityWorkflow(task_name, email, reddit, x_hashtag)
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(handle_signal(workflow)))
    print("\n▶️ Starting workflow...")
    await workflow.run()

if __name__ == "__main__":
    asyncio.run(main())
